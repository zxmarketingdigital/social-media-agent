#!/usr/bin/env python3
"""
instagram_reel_daily.py — publica 1 Reel por dia no seu Instagram, sozinho.

Como funciona:
  1. Pega o proximo video da fila (~/.operacao-ia/data/social-media/reels-queue/).
  2. Le a legenda que VOCE escreveu no arquivo de texto ao lado do video.
  3. Deixa o video disponivel numa URL publica (Bunny Storage, ou a URL que voce
     mesmo colar num arquivo .url) — a API do Instagram nao aceita arquivo local.
  4. Publica como Reel pela API oficial e anota que aquele video ja foi postado.

Convencao da fila (o nome do video manda):
  meu-reel.mp4   o video
  meu-reel.txt   a legenda (OBRIGATORIO — sem ele o video e pulado)
  meu-reel.url   so no modo "manual": a URL publica HTTPS do video

Seguranca e idempotencia:
  - O controle e pelo conteudo do arquivo (SHA-256). Renomear ou reordenar a fila
    NAO faz repostar nada.
  - Se a publicacao ficar INCERTA (o Instagram criou o video mas nao confirmou o
    post), o item e marcado como "ambiguo" e NUNCA e repostado sozinho — para nao
    aparecer duplicado no seu perfil. Voce confere no app e libera com
    --retry-ambiguous.
  - Se a Meta RECUSAR o video (erro claro), isso NAO e ambiguidade: o item volta
    pra fila para nova tentativa depois que voce corrigir o problema.
  - Se o arquivo de controle estiver corrompido, o script NAO publica nada — ele
    prefere parar a arriscar postar duas vezes o mesmo Reel.
  - Fila vazia nao e erro: o script simplesmente nao faz nada.
  - Nenhum token aparece em log, mensagem ou notificacao.

Uso:
  python3 instagram_reel_daily.py                      publica o proximo
  python3 instagram_reel_daily.py --dry-run            mostra tudo, NAO publica
  python3 instagram_reel_daily.py --check              so testa a credencial
  python3 instagram_reel_daily.py --status             mostra a fila e o estado
  python3 instagram_reel_daily.py --retry-ambiguous meu-reel.mp4 \
      --confirmo-que-nao-foi-publicado
  python3 instagram_reel_daily.py --recomecar-controle  (so em caso de arquivo
                                   de controle corrompido — leia o aviso antes)

Compatibilidade: Python 3.9+ (sem sintaxe 3.10+). So biblioteca padrao.
"""

import argparse
import contextlib
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig_common as ig  # noqa: E402

SCRIPT_PATH = Path(__file__).resolve()

LOG_NAME = "ig-publish.log"
JSONL_NAME = "ig-publish.jsonl"

# Limite de caracteres da legenda que conhecemos hoje. A Meta pode mudar — por
# isso a mensagem ao aluno diz "o limite que conhecemos", nunca "o limite e".
CAPTION_MAX = 2200

# "failed" NAO entra aqui de proposito: e falha limpa (a Meta recusou, nada foi
# publicado) e o arquivo tem que voltar a ser candidato na proxima execucao.
PROCESSED = ("posted", "ambiguous", "creating")

# Arquivo que ainda esta sendo copiado pra fila pode ser hasheado pela metade.
# Nesse caso o hash da varredura nao seria o conteudo enviado — e o mesmo video
# voltaria a ser candidato no dia seguinte (post duplicado).
MIN_AGE_SECONDS = 60


class StateCorrupted(RuntimeError):
    """O arquivo de controle existe mas nao da pra ler/entender."""


def log(msg: str, level: str = "INFO") -> None:
    ig.log(msg, level, log_name=LOG_NAME)


# ── estado ────────────────────────────────────────────────────────────────
def load_state() -> Dict:
    """Le o controle do que ja foi postado.

    Arquivo INEXISTENTE = primeira execucao, comeca vazio (normal).
    Arquivo ILEGIVEL = corrupcao. NAO tratamos como "nunca postei nada": isso
    faria a fila inteira ser republicada. Levantamos e quem chama para tudo.
    """
    if not ig.STATE_PATH.exists():
        return {"by_hash": {}}
    try:
        raw = ig.STATE_PATH.read_text()
    except Exception as e:
        raise StateCorrupted("nao consegui ler %s (%s)"
                             % (ig.STATE_PATH, ig.safe_error_repr(e)))
    try:
        data = json.loads(raw)
    except Exception:
        raise StateCorrupted("o conteudo de %s nao e um registro valido"
                             % ig.STATE_PATH)
    if not isinstance(data, dict) or not isinstance(data.get("by_hash", {}), dict):
        raise StateCorrupted("o conteudo de %s esta fora do formato esperado"
                             % ig.STATE_PATH)
    data.setdefault("by_hash", {})
    return data


def save_state(data: Dict) -> None:
    ig.atomic_write(ig.STATE_PATH, json.dumps(data, ensure_ascii=False, indent=2))


def restart_state_control() -> int:
    """Recomeco EXPLICITO do controle, depois de corrupcao. Nunca automatico."""
    if not ig.STATE_PATH.exists():
        print("ℹ️  Nao existe arquivo de controle — o proximo post ja comeca do zero.")
        return 0
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = ig.STATE_PATH.with_name("%s.corrupt-%s" % (ig.STATE_PATH.name, stamp))
    try:
        ig.STATE_PATH.rename(destino)
    except Exception as e:
        print("❌ Nao consegui mover o arquivo de controle: %s" % ig.safe_error_repr(e))
        return 1
    log("controle reiniciado a pedido — antigo guardado em %s" % destino.name, "WARN")
    print("\n✅ Arquivo antigo guardado em: %s" % destino)
    print("\n⚠️  ATENCAO — o historico do que ja foi postado se perdeu.")
    print("   ANTES de deixar a publicacao rodar de novo, tire da fila (%s)"
          % ig.QUEUE_DIR)
    print("   todos os videos que voce JA publicou. Se eles ficarem la, vao ser")
    print("   publicados outra vez.\n")
    return 0


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def already_posted_today(state: Dict) -> Optional[str]:
    """Nome do video que pode ter ido pro ar HOJE (hora local). Trava 1 post/dia.

    Conta 'ambiguous' junto com 'posted' de proposito: ambiguo quer dizer que a
    resposta da Meta se perdeu, e o Reel PODE ter sido publicado. Contar so o
    'posted' abria o furo de o mesmo dia receber 2 Reels reais — o ambiguo era
    pulado, a trava nao disparava e o proximo video ia ao ar por cima dele.
    """
    today = datetime.now().date().isoformat()
    for rec in state.get("by_hash", {}).values():
        status = rec.get("status")
        if status not in ("posted", "ambiguous"):
            continue
        quando = str(rec.get("posted_at") or rec.get("started_at") or "")
        if quando.startswith(today):
            return rec.get("file")
    return None


# ── fila ──────────────────────────────────────────────────────────────────
def list_queue() -> List[Path]:
    if not ig.QUEUE_DIR.exists():
        return []
    return sorted(ig.QUEUE_DIR.glob("*.mp4"))


def read_sidecar(video: Path, suffix: str) -> Optional[str]:
    side = video.with_suffix(suffix)
    if not side.exists():
        return None
    try:
        return side.read_text().strip()
    except Exception:
        return None


def caption_problem(video: Path) -> Optional[str]:
    """Retorna a razao pela qual a legenda nao serve, ou None se estiver ok."""
    caption = read_sidecar(video, ".txt")
    if caption is None:
        return ("falta a legenda: crie o arquivo %s com o texto do post "
                "(nao escrevo legenda no seu lugar)" % video.with_suffix(".txt").name)
    if not caption:
        return "a legenda %s esta vazia" % video.with_suffix(".txt").name
    if len(caption) > CAPTION_MAX:
        return ("a legenda %s tem %s caracteres; o limite que conhecemos e %s — "
                "se a Meta tiver mudado isso, confira a documentacao oficial"
                % (video.with_suffix(".txt").name, len(caption), CAPTION_MAX))
    return None


def hosting_problem(env: Dict[str, str], video: Path) -> Optional[str]:
    """No modo manual, a URL e tao obrigatoria quanto a legenda.

    Se isso so estourasse na hora de publicar, um unico video sem .url travaria
    a fila INTEIRA todos os dias (o script sempre pega o primeiro pronto).
    """
    if provider_of(env) != "manual":
        return None
    url = read_sidecar(video, ".url")
    if not url:
        return ("falta a URL publica: no modo manual crie o arquivo %s com o "
                "link HTTPS do video" % video.with_suffix(".url").name)
    if not ig.is_safe_http_url(url, require_https=True):
        return ("a URL em %s nao serve: precisa comecar com https:// e apontar "
                "para um endereco publico da internet"
                % video.with_suffix(".url").name)
    return None


def hosting_config_problem(env: Dict[str, str]) -> Optional[str]:
    """Problema de CONFIGURACAO (vale pra fila toda), nao de um video."""
    provider = provider_of(env)
    if provider == "manual":
        return None
    if provider != "bunny":
        return ("IG_VIDEO_HOST_PROVIDER=%s nao e suportado. Use 'bunny' ou "
                "'manual'." % provider)
    faltando = [k for k in ("BUNNY_STORAGE_ZONE", "BUNNY_STORAGE_HOST",
                            "BUNNY_STORAGE_PASSWORD", "BUNNY_PULL_HOST")
                if not env.get(k)]
    if faltando:
        return ("faltam dados da hospedagem no Bunny: %s" % ", ".join(faltando))
    return None


def scan_queue(state: Dict,
               env: Dict[str, str]) -> Tuple[List[Tuple[Path, str, str]], List[Tuple[Path, str]]]:
    """Retorna (prontos, pulados).

    prontos = [(video, hash, legenda)] em ordem de nome, so os nao processados.
    pulados = [(video, motivo)] — legenda, URL, arquivo vazio, copia em curso.
    """
    done = state.get("by_hash", {})
    ready = []  # type: List[Tuple[Path, str, str]]
    skipped = []  # type: List[Tuple[Path, str]]
    agora = time.time()
    for p in list_queue():
        try:
            st = p.stat()
            if st.st_size == 0:
                skipped.append((p, "o arquivo de video esta vazio (0 byte)"))
                continue
            idade = agora - st.st_mtime
            if idade < MIN_AGE_SECONDS:
                skipped.append((p, "o arquivo acabou de ser modificado (%ds) — "
                                   "espero a copia terminar; entra na proxima "
                                   "execucao" % int(idade)))
                continue
            h = sha256_of(p)
        except Exception as e:
            skipped.append((p, "nao consegui ler o arquivo (%s)" % ig.safe_error_repr(e)))
            continue
        status = (done.get(h) or {}).get("status")
        if status in PROCESSED:
            if status == "creating":
                # Sobra de uma execucao interrompida no meio. Pode ja estar no ar:
                # NUNCA repostar sozinho.
                log("'%s' ficou pela metade numa execucao anterior — confira no "
                    "Instagram e use --retry-ambiguous se nao publicou" % p.name, "WARN")
            continue
        problem = caption_problem(p) or hosting_problem(env, p)
        if problem:
            skipped.append((p, problem))
            continue
        ready.append((p, h, read_sidecar(p, ".txt") or ""))
    return ready, skipped


# ── hospedagem do video ───────────────────────────────────────────────────
def bunny_upload(env: Dict[str, str], local_path: Path) -> str:
    """Sobe o MP4 pro Bunny Storage e devolve a URL publica."""
    ig.require_keys(env, ["BUNNY_STORAGE_ZONE", "BUNNY_STORAGE_HOST",
                          "BUNNY_STORAGE_PASSWORD", "BUNNY_PULL_HOST"],
                    why="necessarias quando IG_VIDEO_HOST_PROVIDER=bunny")
    zone = env["BUNNY_STORAGE_ZONE"]
    host = env["BUNNY_STORAGE_HOST"]
    key = env["BUNNY_STORAGE_PASSWORD"]
    pull = env["BUNNY_PULL_HOST"]
    folder = env.get("BUNNY_FOLDER", "reels")
    fname = local_path.name
    put_url = "https://%s/%s/%s/%s" % (host, zone, folder, fname)
    req = urllib.request.Request(
        put_url, data=local_path.read_bytes(), method="PUT",
        headers={"AccessKey": key, "Content-Type": "application/octet-stream"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            if r.status not in (200, 201):
                raise ig.IGError("o Bunny respondeu %s ao receber o video" % r.status)
    except ig.IGError:
        raise
    except Exception as e:
        raise ig.IGError("falha ao enviar o video pro Bunny: %s" % ig.safe_error_repr(e))
    return "https://%s/%s/%s" % (pull, folder, fname)


def provider_of(env: Dict[str, str]) -> str:
    return (env.get("IG_VIDEO_HOST_PROVIDER") or "bunny").strip().lower()


def resolve_video_url(env: Dict[str, str], video: Path, dry_run: bool = False) -> str:
    """Descobre (ou cria) a URL publica do video conforme o provedor escolhido."""
    provider = provider_of(env)
    if provider == "manual":
        url = read_sidecar(video, ".url")
        if not url:
            raise ig.ConfigError(
                "no modo manual voce precisa colar a URL publica do video em %s.\n"
                "   A URL tem que ser HTTPS, aberta (sem login) e servir o arquivo "
                "como video." % video.with_suffix(".url").name)
        return url
    if provider == "bunny":
        folder = env.get("BUNNY_FOLDER", "reels")
        pull = env.get("BUNNY_PULL_HOST", "SEU-PULL-HOST")
        if dry_run:
            return "https://%s/%s/%s" % (pull, folder, video.name)
        return bunny_upload(env, video)
    raise ig.ConfigError(
        "IG_VIDEO_HOST_PROVIDER=%s nao e suportado. Use 'bunny' ou 'manual'." % provider)


def wait_public_mp4(url: str, max_attempts: int = 12, sleep: float = 6.0) -> bool:
    """A API do Instagram so aceita URL publica que devolve um video de verdade."""
    if not ig.is_safe_http_url(url, require_https=True):
        log("URL recusada: precisa comecar com https:// e ser publica (%s)"
            % ig.redact_url(url), "ERROR")
        return False
    last = "nenhuma tentativa"
    for attempt in range(1, max_attempts + 1):
        try:
            req = urllib.request.Request(
                url, method="HEAD",
                headers={"User-Agent": "facebookexternalhit/1.1"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                ct = r.headers.get("Content-Type", "")
                if r.status == 200 and "video" in ct:
                    log("URL do video OK em %s tentativa(s) [%s]" % (attempt, ct))
                    return True
                last = "status=%s content-type=%s" % (r.status, ct)
        except Exception as e:
            last = ig.safe_error_repr(e)
        if attempt < max_attempts:
            time.sleep(sleep)
    # Sem a query string: link assinado de storage carrega credencial ali.
    log("a URL do video nao ficou publica a tempo (%s) — ultimo retorno: %s"
        % (ig.redact_url(url), last), "ERROR")
    return False


# ── publicacao ────────────────────────────────────────────────────────────
def publish_reel(ig_user_id: str, token: str, video_url: str, caption: str,
                 share_to_feed: str = "true", creation_cb=None) -> str:
    """Cria o Reel, espera o processamento e publica. Devolve o id do post."""
    log("criando o Reel no Instagram")
    _, payload, headers = ig.http_post(
        "%s/%s/media" % (ig.IG_API, ig_user_id),
        {"media_type": "REELS", "video_url": video_url,
         "caption": caption, "share_to_feed": share_to_feed},
        token=token,
    )
    ig.check_rate_limit(headers)
    creation_id = payload.get("id")
    if not creation_id:
        raise ig.IGError("o Instagram nao devolveu o identificador do Reel: %s"
                         % ig.redact(json.dumps(payload)))
    if creation_cb:
        creation_cb(creation_id)
    # Video demora bem mais que imagem pra processar do lado da Meta.
    ig.wait_container_ready(creation_id, token, max_attempts=15,
                            base_sleep=2.0, max_sleep=30.0)
    log("publicando o Reel")
    _, pub, headers = ig.http_post(
        "%s/%s/media_publish" % (ig.IG_API, ig_user_id),
        {"creation_id": creation_id},
        token=token,
    )
    media_id = pub.get("id")
    if not media_id:
        raise ig.IGError("a publicacao nao foi confirmada: %s"
                         % ig.redact(json.dumps(pub)))
    # O limite so vira AVISO daqui pra frente: a publicacao ja esta confirmada e
    # levantar excecao agora transformaria um sucesso em "publicacao incerta".
    try:
        ig.check_rate_limit(headers)
    except ig.RateLimitExceeded as e:
        log("publiquei, mas o uso do app esta no limite: %s" % e, "WARN")
    return str(media_id)


# ── relatorios ────────────────────────────────────────────────────────────
def print_skipped(skipped: List[Tuple[Path, str]]) -> None:
    for path, reason in skipped:
        print("   ⏭  %s — %s" % (path.name, reason))


def report_skipped(skipped: List[Tuple[Path, str]]) -> None:
    """Registra em LOG e avisa o aluno — mesmo quando outro video foi publicado.

    Sem isto, um Reel sem legenda some da fila em silencio e o aluno so descobre
    semanas depois que aquele post nunca foi ao ar.
    """
    if not skipped:
        return
    for path, reason in skipped:
        log("pulado: %s — %s" % (path.name, reason), "WARN")
        ig.log_jsonl("item_pulado", log_name=JSONL_NAME,
                     file=path.name, motivo=reason)
    ig.notify_local("%s video(s) da fila precisam de ajuste — veja o log."
                    % len(skipped))


def show_status() -> int:
    state = load_state()
    try:
        env = ig.load_ig_env()
    except ig.ConfigError:
        env = {}
    ready, skipped = scan_queue(state, env)
    print("\n📋 Fila de Reels — %s" % ig.QUEUE_DIR)
    if not ig.QUEUE_DIR.exists():
        print("   (a pasta ainda nao existe — rode %s)" % ig.SETUP_HINT)
        return 0
    print("   Prontos para publicar : %s" % len(ready))
    for path, _h, _c in ready[:10]:
        print("      • %s" % path.name)
    if skipped:
        print("   Pulados (precisam de ajuste): %s" % len(skipped))
        print_skipped(skipped)
    counts = {}  # type: Dict[str, int]
    for rec in state.get("by_hash", {}).values():
        st = str(rec.get("status", "?"))
        counts[st] = counts.get(st, 0) + 1
    if counts:
        print("   Historico: %s" % ", ".join("%s=%s" % (k, v) for k, v in sorted(counts.items())))
    posted = already_posted_today(state)
    if posted:
        print("   ⚠️  Ja houve post hoje (%s) — a trava de 1 por dia esta ativa." % posted)
    print("")
    return 0


# ── orquestrador ──────────────────────────────────────────────────────────
def run(dry_run: bool = False, target_name: Optional[str] = None,
        ignore_daily_lock: bool = False, lock_held: bool = False) -> int:
    # A configuracao vem ANTES da fila de proposito: sem credencial nada pode
    # funcionar, e o aluno precisa saber disso mesmo com a fila vazia.
    env = ig.load_ig_env()
    ig.env_secrets(env)
    ig.require_keys(env, ["IG_USER_ID", "IG_ACCESS_TOKEN"])

    if not dry_run:
        # Problema de hospedagem e de CONFIGURACAO — nao pode virar "falha do
        # primeiro video da fila".
        problema = hosting_config_problem(env)
        if problema:
            raise ig.ConfigError("%s\n   Rode %s para completar."
                                 % (problema, ig.SETUP_HINT))

    state = load_state()
    ready, skipped = scan_queue(state, env)

    if target_name:
        ready = [item for item in ready if item[0].name == target_name]
        if not ready:
            print("❌ '%s' nao esta pronto para publicar." % target_name)
            print("   Confira se o arquivo esta em %s e se a legenda existe."
                  % ig.QUEUE_DIR)
            print_skipped([s for s in skipped if s[0].name == target_name])
            return 1

    if not dry_run:
        # Sempre — haja ou nao video pronto. O doc promete log + notificacao.
        report_skipped(skipped)

    if not ready:
        # Fila vazia nao e erro. Mas se algo foi pulado, o aluno precisa saber.
        if skipped:
            print("⏭  Nenhum video pronto para publicar. Itens que precisam de ajuste:")
            print_skipped(skipped)
            log("nenhum video pronto — %s item(ns) precisam de ajuste na fila"
                % len(skipped), "WARN")
        else:
            log("fila vazia — nada a publicar")
        return 0

    pending = len(ready)

    if dry_run:
        video, _fhash, caption = ready[0]
        provider = provider_of(env)
        try:
            url = resolve_video_url(env, video, dry_run=True)
        except ig.ConfigError as e:
            url = "(nao definida) %s" % e
        print("\n" + "=" * 62)
        print("TESTE (--dry-run) — nada foi publicado")
        print("Proximo video : %s" % video.name)
        print("Prontos       : %s" % pending)
        print("Hospedagem    : %s" % provider)
        print("URL do video  : %s" % url)
        print("-" * 62)
        print("LEGENDA:")
        print(caption)
        print("=" * 62)
        if skipped:
            print("Itens pulados:")
            print_skipped(skipped)
        print("")
        return 0

    ig_user_id = env["IG_USER_ID"]
    token = env["IG_ACCESS_TOKEN"]
    share_to_feed = (env.get("IG_SHARE_TO_FEED") or "true").strip().lower()
    if share_to_feed not in ("true", "false"):
        share_to_feed = "true"

    if not ignore_daily_lock:
        posted = already_posted_today(state)
        if posted:
            log("ja publiquei hoje (%s) — nada a fazer (trava de 1 post por dia)"
                % posted)
            return 0

    # Quando o retry manual ja segurou o lock, reusamos ele: pegar de novo
    # daria deadlock, e soltar no meio abriria a janela de post duplicado.
    lock_ctx = contextlib.nullcontext() if lock_held else ig.FileLock("ig-reel-daily")

    try:
        with lock_ctx:
            # Entre a checagem acima e o lock, outra execucao pode ter publicado.
            # Sem esta re-checagem, as duas publicariam = Reel duplicado no perfil.
            state = load_state()
            if not ignore_daily_lock and already_posted_today(state):
                log("ja publiquei hoje (confirmado sob trava) — abortando")
                return 0

            for video, fhash, caption in ready:
                current = (state.get("by_hash", {}).get(fhash) or {}).get("status")
                if current in PROCESSED:
                    log("%s ja foi tratado por outra execucao (%s) — pulando"
                        % (video.name, current))
                    continue

                # O hash foi calculado FORA do lock. Se o arquivo mudou desde
                # entao, o que subiria nao e o que foi identificado — e o mesmo
                # video voltaria como "novo" amanha (post duplicado).
                try:
                    hash_atual = sha256_of(video)
                except Exception as e:
                    log("nao consegui reler %s: %s"
                        % (video.name, ig.safe_error_repr(e)), "WARN")
                    continue
                if hash_atual != fhash:
                    log("%s mudou enquanto eu lia a fila — deixo para a proxima "
                        "execucao" % video.name, "WARN")
                    continue

                try:
                    return _publish_one(env, state, video, fhash, caption,
                                        ig_user_id, token, share_to_feed, pending)
                except ig.ConfigError as e:
                    # Problema local e deterministico daquele item (ex: .url
                    # faltando). Nao gastamos o dia com ele: vai pro proximo.
                    log("pulando %s: %s" % (video.name, ig.redact(e)), "WARN")
                    ig.log_jsonl("item_pulado", log_name=JSONL_NAME,
                                 file=video.name, motivo=ig.redact(e))
                    continue

            log("nenhum video da fila pode ser publicado nesta execucao", "WARN")
            return 1

    except ig.LockBusy as e:
        log("outra execucao ja esta rodando — saindo sem publicar (%s)"
            % ig.safe_error_repr(e), "WARN")
        return 0


def _publish_one(env: Dict[str, str], state: Dict, video: Path, fhash: str,
                 caption: str, ig_user_id: str, token: str, share_to_feed: str,
                 pending: int) -> int:
    """Publica UM video. Ja roda sob o lock e com o estado recem-lido."""
    try:
        log("etapa 1 de 3: deixando o video acessivel por URL publica")
        video_url = resolve_video_url(env, video)
        # Sem a query string: link assinado carrega credencial de bucket.
        log("URL do video: %s" % ig.redact_url(video_url))

        log("etapa 2 de 3: conferindo se a URL ja responde")
        # No modo manual o video ja esta hospedado: nao ha propagacao de CDN
        # para esperar, entao insistir muito so faz o aluno esperar a toa.
        tentativas = 4 if provider_of(env) == "manual" else 12
        if not wait_public_mp4(video_url, max_attempts=tentativas):
            raise ig.IGError(
                "a URL do video nao ficou publica a tempo. Confira se ela abre "
                "no navegador anonimo e se o arquivo e servido como video.")

        def _persist_creation(cid):
            state["by_hash"][fhash] = {
                "file": video.name, "status": "creating",
                "creation_id": cid, "video_url": ig.redact_url(video_url),
                "started_at": datetime.now().isoformat(),
            }
            save_state(state)

        log("etapa 3 de 3: publicando no Instagram")
        media_id = publish_reel(ig_user_id, token, video_url, caption,
                                share_to_feed=share_to_feed,
                                creation_cb=_persist_creation)

        state["by_hash"][fhash] = {
            "file": video.name, "status": "posted",
            "media_id": media_id, "video_url": ig.redact_url(video_url),
            "posted_at": datetime.now().isoformat(),
        }
        save_state(state)
        log("Reel publicado (id do post: %s)" % media_id)
        ig.log_jsonl("reel_publicado", log_name=JSONL_NAME,
                     file=video.name, media_id=media_id)

        remaining = pending - 1
        msg = "Reel publicado: %s. Restam %s na fila." % (video.name, remaining)
        if remaining <= 2:
            msg += " Fila baixa — adicione mais videos."
        ig.notify_local(msg)
        return 0

    except ig.ConfigError:
        # Falha local do item: quem chama decide pular pro proximo. Nao deixamos
        # marca no estado — o arquivo continua candidato.
        state.get("by_hash", {}).pop(fhash, None)
        raise

    except ig.ContainerRejected as e:
        # A Meta RECUSOU o video. Nada foi publicado — isso NAO e ambiguidade.
        # O arquivo volta pra fila para nova tentativa depois da correcao.
        state.get("by_hash", {}).pop(fhash, None)
        save_state(state)
        motivo = ig.safe_error_repr(e)
        log("o Instagram recusou %s: %s" % (video.name, motivo), "ERROR")
        ig.log_jsonl("reel_recusado", log_name=JSONL_NAME,
                     file=video.name, motivo=motivo)
        print("\n❌ O Instagram recusou o video %s." % video.name)
        print("   Motivo: %s" % motivo)
        print("   NADA foi publicado. Depois de corrigir o video (ou o link),")
        print("   ele volta a ser publicado normalmente — nao precisa fazer mais nada.")
        print("   Como investigar: %s" % ig.DOC_HINT)
        ig.notify_local("O Instagram recusou %s — nada foi publicado." % video.name)
        return 1

    except Exception as e:
        current = state.get("by_hash", {}).get(fhash, {}) or {}
        motivo = ig.safe_error_repr(e)
        if current.get("status") == "creating" and current.get("creation_id"):
            # Publicacao INCERTA: o Reel pode ja estar no ar. Nunca repostar sozinho.
            current["status"] = "ambiguous"
            current["error"] = motivo
            state["by_hash"][fhash] = current
            save_state(state)
            log("publicacao INCERTA de %s — NAO vou repostar sozinho para nao "
                "duplicar no seu perfil: %s" % (video.name, motivo), "ERROR")
            print("\n⚠️  A publicacao de %s ficou incerta." % video.name)
            print("   Motivo: %s" % motivo)
            print("   Abra o seu Instagram e confira se o Reel foi publicado.")
            print("   • Se FOI publicado: nao precisa fazer nada.")
            print("   • Se NAO foi: me peca para republicar. O comando e")
            print("     python3 %s --retry-ambiguous %s --confirmo-que-nao-foi-publicado"
                  % (SCRIPT_PATH, video.name))
            ig.notify_local("Publicacao de %s ficou incerta — confira o perfil."
                            % video.name)
            return 1
        log("nao consegui publicar %s: %s" % (video.name, motivo), "ERROR")
        print("\n❌ Nao consegui publicar %s." % video.name)
        print("   Motivo: %s" % motivo)
        print("   Erros comuns e como resolver: %s" % ig.DOC_HINT)
        ig.notify_local("Falha ao publicar %s." % video.name)
        return 1


# ── retry manual de publicacao incerta ────────────────────────────────────
def _explicar_ambiguidade(file_name: str) -> None:
    print("\n⚠️  Confirmacao necessaria antes de tentar de novo")
    print("   Video: %s" % file_name)
    print("   Este Reel PODE ja estar publicado no seu Instagram.")
    print("   Abra o app, olhe o seu perfil e confirme que ele NAO esta la.")
    print("   Se publicar de novo sem conferir, o post aparece duplicado.\n")


def retry_ambiguous(file_name: str, confirmado: bool = False) -> int:
    video = ig.QUEUE_DIR / file_name
    if not video.exists():
        print("❌ Nao encontrei %s em %s" % (file_name, ig.QUEUE_DIR))
        return 1

    _explicar_ambiguidade(file_name)

    if confirmado:
        origem = "confirmacao explicita do aluno (--confirmo-que-nao-foi-publicado)"
    elif sys.stdin.isatty():
        try:
            answer = input('   Digite SIM (maiusculo) se o Reel NAO esta no seu perfil: ').strip()
        except (EOFError, KeyboardInterrupt):
            print("\n   Cancelado — nada foi publicado.")
            return 1
        if answer != "SIM":
            print("   Cancelado — nada foi publicado.")
            return 1
        origem = "confirmacao digitada no terminal"
    else:
        # Sem terminal (e o caso do Claude rodando por voce): a confirmacao vem
        # do aluno no chat e chega aqui como flag. Nunca publicamos sem ela.
        print("❌ Falta a sua confirmacao de que o Reel NAO esta no perfil.")
        print("   Confira o seu Instagram e responda no chat. Depois disso o")
        print("   comando a rodar e:")
        print("   python3 %s --retry-ambiguous %s --confirmo-que-nao-foi-publicado"
              % (SCRIPT_PATH, file_name))
        return 1

    # O lock precisa cobrir ler -> apagar -> republicar. Fora dele, a publicacao
    # diaria pode gravar entre a leitura e a escrita e ter o registro apagado.
    with ig.FileLock("ig-reel-daily"):
        state = load_state()
        match = None
        for h, rec in state.get("by_hash", {}).items():
            if rec.get("file") == file_name and rec.get("status") in ("ambiguous", "creating"):
                match = h
                break
        if match is None:
            print("ℹ️  '%s' nao esta marcado como publicacao incerta." % file_name)
            print("   Veja a situacao da fila com: --status")
            return 1
        state["by_hash"].pop(match, None)
        save_state(state)
        log("liberado manualmente para nova tentativa: %s (%s)"
            % (file_name, origem), "WARN")
        ig.log_jsonl("retry_ambiguo_autorizado", log_name=JSONL_NAME,
                     file=file_name, confirmacao=origem)
        return run(target_name=file_name, ignore_daily_lock=True, lock_held=True)


# ── CLI ───────────────────────────────────────────────────────────────────
def check_only() -> int:
    env = ig.load_ig_env()
    ig.env_secrets(env)
    ig.require_keys(env, ["IG_USER_ID", "IG_ACCESS_TOKEN"])
    username = ig.validate_credentials(env["IG_USER_ID"], env["IG_ACCESS_TOKEN"])
    print("✅ Conectado ao Instagram: @%s" % username)
    return 0


def main() -> int:
    # allow_abbrev=False: `--retry-amb` nao pode virar `--retry-ambiguous` por
    # prefixo, nem um `--confirmo` truncado autorizar uma republicacao.
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Publica 1 Reel por dia no Instagram a partir de uma fila local.")
    parser.add_argument("--dry-run", action="store_true",
                        help="mostra o que seria publicado, sem publicar nada")
    parser.add_argument("--check", action="store_true",
                        help="so testa a credencial e mostra a conta conectada")
    parser.add_argument("--status", action="store_true",
                        help="mostra a fila e o historico")
    parser.add_argument("--retry-ambiguous", metavar="ARQUIVO.mp4", default=None,
                        help="tenta de novo uma publicacao que ficou incerta "
                             "(exige a sua confirmacao)")
    parser.add_argument("--confirmo-que-nao-foi-publicado", action="store_true",
                        help="confirma que voce conferiu o perfil e o Reel NAO "
                             "esta la (usar junto com --retry-ambiguous)")
    parser.add_argument("--recomecar-controle", action="store_true",
                        help="guarda o arquivo de controle corrompido e recomeca "
                             "o historico do zero (leia o aviso antes)")
    args = parser.parse_args()

    try:
        if args.recomecar_controle:
            return restart_state_control()
        if args.status:
            return show_status()
        if args.check:
            return check_only()
        if args.retry_ambiguous:
            return retry_ambiguous(args.retry_ambiguous,
                                   confirmado=args.confirmo_que_nao_foi_publicado)
        return run(dry_run=args.dry_run)
    except StateCorrupted as e:
        print("\n⛔ Nao vou publicar agora — nao consigo confirmar o que ja foi postado.")
        print("   %s" % ig.redact(e))
        print("   Parar aqui e de proposito: sem esse registro, eu poderia postar")
        print("   de novo videos que ja estao no seu perfil.")
        print("   Para recomecar o controle do zero (e ai TIRE da fila o que ja")
        print("   foi publicado), o comando e:")
        print("   python3 %s --recomecar-controle\n" % SCRIPT_PATH)
        try:
            log("estado corrompido — publicacao abortada: %s" % ig.redact(e), "ERROR")
            ig.notify_local("Publicacao pausada: o controle de posts esta corrompido.")
        except Exception:
            pass
        return 4
    except ig.ConfigError as e:
        print("\n⚠️  %s\n" % ig.redact(e))
        return 2
    except ig.RateLimitExceeded as e:
        print("\n⚠️  %s\n" % ig.redact(e))
        return 3
    except ig.IGError as e:
        print("\n❌ O Instagram recusou a operacao.")
        print("   Motivo: %s" % ig.redact(e))
        print("   Erros comuns e como resolver: %s\n" % ig.DOC_HINT)
        return 1
    except KeyboardInterrupt:
        print("\nCancelado.")
        return 130
    except Exception as e:
        # Rede de seguranca: o aluno nunca deve ver um traceback do Python.
        print("\n❌ Algo deu errado ao publicar.")
        print("   Detalhe: %s" % ig.safe_error_repr(e))
        print("   Erros comuns e como resolver: %s\n" % ig.DOC_HINT)
        try:
            log("erro inesperado: %s" % ig.safe_error_repr(e), "ERROR")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
