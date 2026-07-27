#!/usr/bin/env python3
"""
ig_common.py — helpers compartilhados da publicacao automatica no Instagram.

Usado por instagram_reel_daily.py (publica 1 Reel/dia) e por
instagram_token_refresh.py (mantem o token de 60 dias vivo).

So biblioteca padrao do Python. Nada aqui faz rede sem o token do proprio aluno.

Onde ficam as coisas (tudo FORA do repositorio, na pasta do aluno):
  ~/.operacao-ia/config/instagram.env          credencial (chmod 600)
  ~/.operacao-ia/data/social-media/reels-queue fila de MP4 + legendas
  ~/.operacao-ia/data/social-media/*.json      estado (o que ja foi postado)
  ~/.operacao-ia/logs/                         logs

Compatibilidade: escrito para rodar em Python 3.9+ (sem sintaxe 3.10+).
"""

try:
    import fcntl
except ImportError:  # Windows/Linux sem POSIX locks: o doc promete uso manual
    fcntl = None     # o FileLock cai pro modo O_EXCL, que e portatil
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

# ── endpoints ─────────────────────────────────────────────────────────────
# Instagram API with Instagram Login (host graph.instagram.com).
IG_API = "https://graph.instagram.com/v21.0"
IG_REFRESH_URL = "https://graph.instagram.com/refresh_access_token"

# ── caminhos ──────────────────────────────────────────────────────────────
HOME = Path.home()
OPERACAO_DIR = HOME / ".operacao-ia"
CONFIG_DIR = OPERACAO_DIR / "config"
ENV_PATH = CONFIG_DIR / "instagram.env"
DATA_DIR = OPERACAO_DIR / "data" / "social-media"
QUEUE_DIR = DATA_DIR / "reels-queue"
STATE_PATH = DATA_DIR / "ig-publish-state.json"
LOCK_DIR = DATA_DIR / ".locks"
# Idade a partir da qual um arquivo de lock e considerado orfao (so no
# fallback sem fcntl — com flock o SO libera sozinho quando o processo morre).
# 2h cobre com folga o pior caso: upload lento + poll de Reels de ~5min.
STALE_LOCK_S = 2 * 60 * 60
LOG_DIR = OPERACAO_DIR / "logs"

DOC_HINT = "docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md"
SETUP_HINT = "python3 setup/setup_publicacao_ig.py"


# ── excecoes ──────────────────────────────────────────────────────────────
class ConfigError(Exception):
    """Falta configuracao (arquivo, chave). Mensagem ja e legivel pro aluno."""


class IGError(RuntimeError):
    """Erro vindo da API do Instagram/Meta."""


class IGTransientError(IGError):
    """Falha de TRANSPORTE (rede caiu, timeout, DNS) — nao e resposta da Meta.

    Importa muito distinguir: um timeout no meio do acompanhamento do video NAO
    significa que a Meta rejeitou nada, entao vale a pena tentar de novo.
    """


class ContainerRejected(IGError):
    """A Meta RECUSOU o video (status ERROR/EXPIRED).

    E uma falha DEFINITIVA e conhecida: o Reel com certeza NAO foi publicado.
    Quem trata isso pode liberar o arquivo para nova tentativa sem risco de
    duplicar post — ao contrario de uma publicacao de resultado incerto.
    """


class RateLimitExceeded(RuntimeError):
    """Hard-stop quando o uso do app passa do limite seguro."""


class LockBusy(RuntimeError):
    """Outra execucao ja esta rodando."""


# ── redaction de segredo ──────────────────────────────────────────────────
# Padroes que NUNCA podem vazar em log, notificacao ou mensagem de erro.
_SECRET_PATTERNS = [
    re.compile(r"access_token=([^&\s\"']+)", re.IGNORECASE),
    re.compile(r"\"access_token\"\s*:\s*\"([^\"]+)\""),
    re.compile(r"Bearer\s+([A-Za-z0-9._\-]+)", re.IGNORECASE),
    re.compile(r"apikey=([^&\s\"']+)", re.IGNORECASE),
    re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
    re.compile(r"IGAA[A-Za-z0-9_\-]{30,}"),
    re.compile(r"AccessKey['\"]?\s*[:=]\s*([^\s,'\"}]+)", re.IGNORECASE),
]

# Valores literais registrados em runtime (o token do aluno pode nao comecar
# com IGAA — registrar o valor exato garante a redaction em qualquer formato).
_RUNTIME_SECRETS = []  # type: List[str]


def register_secret(value: Optional[str]) -> None:
    """Registra um valor sensivel para ser mascarado em qualquer saida."""
    if not value:
        return
    v = str(value).strip()
    if len(v) < 12:
        return
    if v not in _RUNTIME_SECRETS:
        _RUNTIME_SECRETS.append(v)


def _mask(m) -> str:
    whole = m.group(0)
    if "=" in whole:
        return whole.split("=")[0] + "=<redacted>"
    return "<redacted>"


def redact(text: Any) -> str:
    """Substitui segredos por <redacted>. Idempotente e sempre retorna str."""
    if text is None:
        return ""
    out = str(text)
    if not out:
        return out
    for secret in _RUNTIME_SECRETS:
        out = out.replace(secret, "<redacted>")
    for pat in _SECRET_PATTERNS:
        out = pat.sub(_mask, out)
    return out


def safe_error_repr(e: BaseException) -> str:
    """Representacao de excecao com segredos mascarados. Usar SEMPRE em log."""
    return redact("%s: %s" % (type(e).__name__, e))


def redact_url(url: Any) -> str:
    """URL sem a query string.

    Link assinado de storage (R2/S3/Bunny com token) carrega a credencial na
    query string — `?X-Amz-Signature=...`, `?token=...`. redact() nao cobre isso
    (os padroes sao de token da Meta), entao a query inteira sai da saida.
    """
    raw = str(url or "")
    if not raw:
        return ""
    try:
        p = urlparse(raw)
    except Exception:
        return "<url>"
    if not p.scheme or not p.netloc:
        return redact(raw)
    base = "%s://%s%s" % (p.scheme, p.netloc, p.path)
    if p.query or p.fragment:
        base += "?<omitido>"
    return redact(base)


# ── log ───────────────────────────────────────────────────────────────────
def _ts() -> str:
    # Hora LOCAL da maquina do aluno (nao fixamos fuso do Brasil).
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _open_private_log(log_name: str):
    """Abre o arquivo de log garantindo permissao restrita na CRIACAO.

    O log pode conter nome de arquivo, host e mensagem de erro da Meta — nada
    que deva ficar legivel por outros usuarios/processos da maquina.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(str(LOG_DIR), 0o700)
    except OSError:
        pass
    target = LOG_DIR / log_name
    existed = target.exists()
    fh = target.open("a")
    if not existed:
        try:
            os.chmod(str(target), 0o600)
        except OSError:
            pass
    return fh


def log(msg: str, level: str = "INFO", log_name: str = "ig-publish.log") -> None:
    line = "[%s] [%s] %s" % (_ts(), level, redact(msg))
    print(line, flush=True)
    try:
        with _open_private_log(log_name) as f:
            f.write(line + "\n")
    except Exception:
        pass  # log nunca derruba a execucao


def log_jsonl(event: str, log_name: str = "ig-publish.jsonl", **kwargs) -> None:
    try:
        safe = {}
        for k, v in kwargs.items():
            safe[k] = redact(v) if isinstance(v, str) else v
        rec = {"ts": datetime.now().isoformat(), "event": event}
        rec.update(safe)
        with _open_private_log(log_name) as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── notificacao local (macOS) ─────────────────────────────────────────────
def notify_local(message: str, title: str = "Social Media Agent") -> None:
    """Notificacao nativa do macOS. Best-effort: nunca derruba a execucao."""
    if sys.platform != "darwin":
        return
    try:
        body = redact(message)
        body = body.replace("\\", " ").replace('"', "'").replace("\n", " ")
        head = str(title).replace("\\", " ").replace('"', "'")
        script = 'display notification "%s" with title "%s"' % (body[:220], head[:60])
        subprocess.run(["osascript", "-e", script], timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ── env ───────────────────────────────────────────────────────────────────
def load_ig_env(path: Optional[Path] = None) -> Dict[str, str]:
    """Le o instagram.env do aluno. Erro legivel (nunca traceback) se faltar."""
    target = path or ENV_PATH
    if not target.exists():
        raise ConfigError(
            "Nao encontrei a configuracao do Instagram em %s.\n"
            "   A publicacao automatica ainda nao foi ativada nesta maquina.\n"
            "   Para ativar, rode: %s\n"
            "   Passo a passo completo: %s" % (target, SETUP_HINT, DOC_HINT)
        )
    env = {}  # type: Dict[str, str]
    for line in target.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def require_keys(env: Dict[str, str], keys: List[str],
                 why: str = "") -> None:
    """Falha com o nome EXATO da chave faltando (sem traceback)."""
    missing = [k for k in keys if not env.get(k)]
    if not missing:
        return
    extra = ("\n   (%s)" % why) if why else ""
    raise ConfigError(
        "Faltando em %s: %s%s\n"
        "   Rode %s para preencher, ou veja %s"
        % (ENV_PATH, ", ".join(missing), extra, SETUP_HINT, DOC_HINT)
    )


def env_secrets(env: Dict[str, str]) -> None:
    """Registra os valores sensiveis do env para redaction automatica."""
    for key in ("IG_ACCESS_TOKEN", "BUNNY_STORAGE_PASSWORD", "IG_APP_SECRET"):
        register_secret(env.get(key))


# ── escrita atomica ───────────────────────────────────────────────────────
def atomic_write(path: Path, content: str, mode: int = 0o600) -> None:
    """Grava sem deixar arquivo pela metade se o processo morrer no meio.

    O fsync antes do os.replace nao e detalhe: sem ele, um desligamento no botao
    (ou travamento) pode deixar o arquivo renomeado com 0 byte depois do boot —
    e o estado de publicacao com 0 byte e exatamente o que faria o script achar
    que nunca postou nada.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".ig-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
        try:  # durabilidade do proprio rename
            dir_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ── lock ──────────────────────────────────────────────────────────────────
class FileLock:
    """Impede que duas execucoes publiquem ao mesmo tempo (post duplicado)."""

    def __init__(self, name: str):
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOCK_DIR / ("%s.lock" % name)
        self.fh = None
        self.fd = None

    def __enter__(self):
        if fcntl is None:
            # Sem POSIX locks (Windows): O_EXCL da exclusao mutua de verdade.
            # Um lock orfao (processo morto sem limpar) e liberado depois de
            # STALE_LOCK_S — melhor que travar a fila do aluno pra sempre.
            try:
                self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                idade = time.time() - self.path.stat().st_mtime
                if idade < STALE_LOCK_S:
                    raise LockBusy("outra execucao ja esta rodando (%s)" % self.path)
                self.path.unlink()
                self.fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            return self

        self.fh = self.path.open("w")
        try:
            fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.fh.close()
            self.fh = None
            raise LockBusy("outra execucao ja esta rodando (%s)" % self.path)
        return self

    def __exit__(self, *_):
        if self.fd is not None:
            try:
                os.close(self.fd)
                self.path.unlink()
            except OSError:
                pass
            self.fd = None
            return
        if self.fh:
            try:
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
            finally:
                self.fh.close()
                self.fh = None


# ── HTTP ──────────────────────────────────────────────────────────────────
def _http_request(url: str, method: str, token: Optional[str] = None,
                  data: Optional[Dict[str, Any]] = None,
                  timeout: int = 30) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    """GET/POST com Authorization Bearer no header — NUNCA token na URL.

    Sanitiza qualquer corpo de erro antes de levantar a excecao.
    """
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer %s" % token
    body = None
    if data:
        clean = {}
        for k, v in data.items():
            if k == "access_token":
                continue  # token vai no header, jamais no corpo/URL
            clean[k] = v
        if method == "POST":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            body = urlencode(clean).encode()
        else:
            url = url + ("&" if "?" in url else "?") + urlencode(clean)
    req = Request(url, data=body, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
            return r.status, payload, dict(r.headers)
    except HTTPError as e:
        # A Meta RESPONDEU (com erro). O corpo traz a causa real e o code.
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        raise IGError("HTTP %s em %s: %s" % (
            getattr(e, "code", "?"), redact_url(url),
            redact(body_text) or redact(e)))
    except OSError as e:
        # Rede/DNS/timeout: a Meta nem foi consultada. Erro TRANSITORIO.
        raise IGTransientError("nao consegui falar com %s: %s"
                               % (redact_url(url), safe_error_repr(e)))
    except Exception as e:
        raise IGError("resposta inesperada de %s: %s"
                      % (redact_url(url), safe_error_repr(e)))


def http_post(url: str, data: Dict[str, Any], timeout: int = 30,
              token: Optional[str] = None) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    if token is None and data:
        token = data.get("access_token")
    return _http_request(url, "POST", token=token, data=data, timeout=timeout)


def http_get(url: str, token: Optional[str] = None, timeout: int = 10,
             params: Optional[Dict[str, Any]] = None
             ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    return _http_request(url, "GET", token=token, data=params, timeout=timeout)


def check_rate_limit(headers: Dict[str, str], hard: int = 90, warn: int = 80) -> None:
    """Aviso acima de 80% de uso do app; para de vez acima de 90%."""
    usage = headers.get("X-App-Usage") or headers.get("x-app-usage")
    if not usage:
        return
    try:
        u = json.loads(usage)
    except Exception:
        return
    call_count = u.get("call_count", 0)
    if call_count >= hard:
        raise RateLimitExceeded(
            "uso do app em %s%% (limite %s%%) — parando de proposito para o "
            "Instagram nao bloquear sua conta. Tente de novo daqui algumas horas."
            % (call_count, hard))
    if call_count >= warn:
        log("uso do app em %s%% — perto do limite" % call_count, "WARN")


# ── URL publica ───────────────────────────────────────────────────────────
def is_safe_http_url(url: str, require_https: bool = False) -> bool:
    """So aceita http/https com host publico (bloqueia localhost e afins).

    require_https=True para a URL que vai pra Meta: o doc e o setup prometem
    HTTPS ao aluno, e um link http passaria no guard local so pra ser recusado
    la na frente, com mensagem muito pior.
    """
    try:
        p = urlparse(url)
    except Exception:
        return False
    allowed = ("https",) if require_https else ("http", "https")
    if p.scheme not in allowed:
        return False
    if not p.hostname:
        return False
    if p.hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return False
    return True


# ── container de midia ────────────────────────────────────────────────────
def wait_container_ready(creation_id: str, token: str, max_attempts: int = 8,
                         base_sleep: float = 1.5, max_sleep: float = 20.0) -> None:
    """Aguarda o Instagram terminar de processar o video (status FINISHED)."""
    url = "%s/%s" % (IG_API, creation_id)
    for attempt in range(1, max_attempts + 1):
        try:
            _, payload, _ = http_get(url, token=token,
                                     params={"fields": "status_code,status"})
            status_code = payload.get("status_code")
            if status_code == "FINISHED":
                log("video processado em %s tentativa(s)" % attempt)
                return
            if status_code in ("ERROR", "EXPIRED"):
                # A Meta RECUSOU. O Reel com certeza NAO foi publicado.
                raise ContainerRejected(
                    "o Instagram recusou o video (%s). Causa mais comum: a URL do "
                    "video nao esta publica, ou o arquivo esta fora das specs de "
                    "Reels. Detalhe: %s" % (status_code, redact(json.dumps(payload))))
        except ContainerRejected:
            raise
        except IGTransientError as e:
            # Rede oscilou no meio do acompanhamento — NAO e recusa da Meta.
            # Sem este ramo, uma queda de 3s abortaria um video que estava OK.
            log("rede instavel checando processamento (tentativa %s): %s"
                % (attempt, safe_error_repr(e)), "WARN")
        except IGError:
            raise
        except Exception as e:
            log("checando processamento (tentativa %s): %s"
                % (attempt, safe_error_repr(e)), "WARN")
        if attempt < max_attempts:
            time.sleep(min(base_sleep * (2 ** (attempt - 1)), max_sleep))
    raise IGError("o Instagram nao terminou de processar o video depois de %s "
                  "tentativas" % max_attempts)


# ── validacao de credencial ───────────────────────────────────────────────
def validate_credentials(ig_user_id: str, token: str) -> str:
    """Le a conta conectada (nao publica nada). Retorna o @username."""
    if not ig_user_id or not token:
        raise ConfigError("IG_USER_ID e IG_ACCESS_TOKEN sao obrigatorios.")
    register_secret(token)
    _, payload, headers = http_get("%s/%s" % (IG_API, ig_user_id), token=token,
                                   params={"fields": "id,username"}, timeout=20)
    try:
        check_rate_limit(headers)
    except RateLimitExceeded:
        raise
    username = payload.get("username")
    if not username:
        raise IGError("a Meta respondeu sem o nome de usuario (campos: %s). "
                      "Confira se o IG_USER_ID e o da conta certa."
                      % list(payload.keys()))
    return str(username)


def resolve_user_id(token: str) -> Tuple[str, str]:
    """Descobre o IG_USER_ID a partir do token. Retorna (id, username).

    Existe porque achar o ID numerico na tela da Meta e o passo em que mais
    gente trava — e porque prometer isso no guia sem implementar obrigaria o
    Claude a improvisar um curl com o token na linha de comando.

    [VERIFICAR] este endpoint nao e exercitado pelo pipeline de producao (so o
    publish e o refresh sao). Se ele nao responder, o setup continua pedindo o
    ID na mao — nunca trava por causa disto.
    """
    if not token:
        raise ConfigError("preciso do token para descobrir o ID da conta.")
    register_secret(token)
    _, payload, _ = http_get("%s/me" % IG_API, token=token,
                             params={"fields": "user_id,username"}, timeout=20)
    user_id = payload.get("user_id") or payload.get("id")
    username = payload.get("username") or ""
    if not user_id:
        raise IGError("a Meta respondeu sem o ID da conta (campos: %s)."
                      % list(payload.keys()))
    return str(user_id), str(username)
