#!/usr/bin/env python3
"""
Setup 7 — Bônus opcional: Publicação Automática no Instagram.

NÃO faz parte das 8 etapas. Pode ser rodado a qualquer momento (inclusive
semanas depois) e pular não afeta nada do setup.

O que ele faz, nesta ordem:
  1. Explica o que é e confere se a conta é Business/Creator
  2. Coleta IG_USER_ID e IG_ACCESS_TOKEN (nunca mostra o token de volta)
  3. VALIDA a credencial ao vivo e mostra o @username conectado pra confirmação
  4. Pergunta onde o vídeo vai ficar hospedado (Bunny automático ou manual)
  5. Grava ~/.operacao-ia/config/instagram.env com chmod 600
  6. Cria a fila e roda um teste sem publicar (--dry-run)
  7. SÓ ENTÃO, com um "sim" explícito, agenda a publicação diária no macOS

Rodar de novo é seguro: nada é duplicado e nada é sobrescrito sem perguntar.
Para desativar o agendamento: python3 setup/setup_publicacao_ig.py --uninstall

Guia completo: docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md
"""
import argparse
import getpass
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOMATIONS = REPO_ROOT / "automations" / "instagram"
sys.path.insert(0, str(AUTOMATIONS))

HOME = Path.home()
OPERACAO = HOME / ".operacao-ia"
CONFIG = OPERACAO / "config"
IG_ENV = CONFIG / "instagram.env"
CONFIG_JSON = CONFIG / "config.json"
QUEUE_DIR = OPERACAO / "data" / "social-media" / "reels-queue"
LOG_DIR = OPERACAO / "logs"
LAUNCH_AGENTS = HOME / "Library" / "LaunchAgents"

PUBLISHER = AUTOMATIONS / "instagram_reel_daily.py"
REFRESHER = AUTOMATIONS / "instagram_token_refresh.py"

AGENTS = [
    ("com.socialmediaagent.ig-reel-daily", PUBLISHER),
    ("com.socialmediaagent.ig-token-refresh", REFRESHER),
]

DOC = "docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md"


def erro_seguro(e):
    """Descrição do erro com qualquer credencial mascarada."""
    bruto = "%s: %s" % (type(e).__name__, e)
    try:
        import ig_common
        return ig_common.redact(bruto)
    except Exception:
        return bruto


def prompt(msg, default=""):
    """Pergunta simples.

    Ctrl+C NAO cai no default: com quase todo default afirmativo, engolir o
    KeyboardInterrupt fazia "sair no meio" virar "aceitar tudo" — inclusive
    agendar publicacao no perfil de quem tinha acabado de desistir.
    """
    suffix = " [%s]" % default if default else ""
    try:
        ans = input("%s%s: " % (msg, suffix)).strip()
    except EOFError:
        print()
        return default
    except KeyboardInterrupt:
        print()
        raise
    return ans or default


def prompt_secreto(msg):
    """Pergunta CREDENCIAL: o que o aluno digita/cola NAO aparece na tela.

    input() comum ecoa o token no terminal e na transcricao da sessao, o que
    contraria a regra "nunca mostre tokens" do proprio Setup. getpass usa o
    TTY quando existe; sem TTY (rodando por subprocesso) ele avisa antes de
    cair no input() eco-ado, em vez de vazar em silencio.
    """
    try:
        return getpass.getpass("%s: " % msg).strip()
    except (EOFError, getpass.GetPassWarning):
        print("   (nao consegui esconder o que voce digita neste terminal —")
        print("    se preferir nao arriscar, rode este setup numa janela normal)")
        try:
            return input("%s: " % msg).strip()
        except EOFError:
            print()
            return ""


def confirmar(msg):
    """Pergunta IRREVERSIVEL: so segue com um sim digitado. Default = nao."""
    return sim(prompt("%s (s/n)" % msg, "nao"))


def sim(resposta):
    return str(resposta).strip().lower().startswith("s")


def mascara(valor):
    v = str(valor or "")
    if len(v) <= 4:
        return "****"
    return "termina em ...%s (%s caracteres)" % (v[-4:], len(v))


# ── env do aluno ──────────────────────────────────────────────────────────
def ler_env():
    dados = {}
    if not IG_ENV.exists():
        return dados
    try:
        for linha in IG_ENV.read_text().splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            k, v = linha.split("=", 1)
            dados[k.strip()] = v.strip().strip('"').strip("'")
    except Exception as e:
        print("⚠️  Não consegui ler %s (%s) — vou recriar." % (IG_ENV, e))
    return dados


def backup_env():
    """Copia de segurança do instagram.env antes de sobrescrever."""
    if not IG_ENV.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = IG_ENV.parent / ("%s.bak.%s" % (IG_ENV.name, stamp))
    try:
        conteudo = IG_ENV.read_text()
    except Exception:
        return None
    try:
        import ig_common
        ig_common.atomic_write(destino, conteudo, mode=0o600)
    except Exception:
        try:
            destino.write_text(conteudo)
            destino.chmod(0o600)
        except Exception:
            return None
    return destino


def gravar_env(pares, env_atual=None):
    """Grava o instagram.env com permissão 600 desde a criação.

    Duas coisas importam aqui:
      • o arquivo nasce 0600 (via arquivo temporário), em vez de nascer 0644 e
        só depois receber chmod — não existe janela em que o token fique legível
        por outros processos da máquina;
      • chaves que o setup não conhece (ex: IG_APP_SECRET que o aluno guardou)
        são PRESERVADAS, em vez de sumirem sem aviso.
    """
    CONFIG.mkdir(parents=True, exist_ok=True)
    conhecidas = [c for c, _v in pares]
    extras = []
    for chave, valor in (env_atual or {}).items():
        if chave not in conhecidas:
            extras.append((chave, valor))

    linhas = ["# Publicação automática no Instagram — gerado por setup_publicacao_ig.py",
              "# Gerado em %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "# NÃO versione este arquivo. Ele guarda a sua credencial.",
              ""]
    for chave, valor in pares:
        linhas.append(chave + "=" + str(valor if valor is not None else ""))
    if extras:
        linhas.append("")
        linhas.append("# Chaves que já estavam no seu arquivo (preservadas):")
        for chave, valor in extras:
            linhas.append(chave + "=" + str(valor))
    conteudo = "\n".join(linhas) + "\n"

    escrito_seguro = False
    try:
        import ig_common
        ig_common.atomic_write(IG_ENV, conteudo, mode=0o600)
        escrito_seguro = True
    except Exception:
        IG_ENV.write_text(conteudo)
        try:
            IG_ENV.chmod(0o600)
        except Exception:
            pass

    # Só afirma "só você consegue ler" depois de CONFERIR o modo no disco.
    modo = None
    try:
        modo = IG_ENV.stat().st_mode & 0o777
    except Exception:
        pass
    if modo == 0o600:
        print("✅ Configuração salva em %s (só você consegue ler)" % IG_ENV)
    else:
        print("✅ Configuração salva em %s" % IG_ENV)
        print("⚠️  ATENÇÃO: não consegui deixar o arquivo restrito a você")
        print("    (permissão atual: %s). Isso acontece em pastas sincronizadas"
              % (oct(modo) if modo is not None else "desconhecida"))
        print("    ou discos sem suporte a permissão do macOS. O seu token está")
        print("    legível por outros programas da máquina — considere mover a")
        print("    pasta ~/.operacao-ia para um disco local.")
    return escrito_seguro


# ── config.json (namespace próprio, nunca toca phase_completed) ───────────
def marcar_config(configurado, agendado):
    dados = {}
    if CONFIG_JSON.exists():
        try:
            carregado = json.loads(CONFIG_JSON.read_text())
            if isinstance(carregado, dict):
                dados = carregado
        except Exception:
            print("⚠️  config.json ilegível — não vou mexer nele para não perder"
                  " o progresso das etapas.")
            return
    dados["ig_auto_publish"] = {
        "configured": bool(configurado),
        "enabled": bool(agendado),
        "configured_at": datetime.now().isoformat(),
    }
    try:
        CONFIG.mkdir(parents=True, exist_ok=True)
        CONFIG_JSON.write_text(json.dumps(dados, indent=2, ensure_ascii=False))
    except Exception as e:
        print("⚠️  Não consegui atualizar o config.json (%s) — sem problema," % e)
        print("    isso não afeta a publicação.")


# ── LaunchAgents ──────────────────────────────────────────────────────────
def caminho_plist(label):
    return LAUNCH_AGENTS / ("%s.plist" % label)


def descarregar(label):
    """Remove o agendamento atual, se existir. Silencioso se não existir."""
    alvo = "gui/%s/%s" % (os.getuid(), label)
    subprocess.run(["launchctl", "bootout", alvo],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    plist = caminho_plist(label)
    if plist.exists():
        subprocess.run(["launchctl", "unload", "-w", str(plist)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def carregar(label):
    """Ativa o agendamento. Tenta o comando novo e cai no antigo se preciso."""
    plist = caminho_plist(label)
    dominio = "gui/%s" % os.getuid()
    r = subprocess.run(["launchctl", "bootstrap", dominio, str(plist)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return True
    r2 = subprocess.run(["launchctl", "load", "-w", str(plist)],
                        capture_output=True, text=True)
    if r2.returncode == 0:
        return True
    print("⚠️  Não consegui ativar %s automaticamente." % label)
    detalhe = (r.stderr or r2.stderr or "").strip()
    if detalhe:
        print("    Detalhe do sistema: %s" % detalhe[:200])
    return False


def renderizar_plists(hora, minuto):
    """Instala os 2 agendamentos. Retorna {label: True/False} — por agente.

    Um booleano só para os dois mentia nos dois sentidos: dizia "não ativei" com
    o publicador ativo publicando, e escondia que a renovação do token tinha
    ficado de fora (o que mata a publicação silenciosamente em 60 dias).
    """
    LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    resultado = {}
    for label, script in AGENTS:
        molde = AUTOMATIONS / ("%s.plist.template" % label)
        if not molde.exists():
            print("❌ Molde não encontrado: %s" % molde)
            resultado[label] = False
            continue
        texto = molde.read_text()
        texto = texto.replace("__PYTHON__", sys.executable)
        texto = texto.replace("__SCRIPT__", str(script))
        texto = texto.replace("__HOUR__", str(hora))
        texto = texto.replace("__MINUTE__", str(minuto))
        texto = texto.replace("__LOGDIR__", str(LOG_DIR))
        descarregar(label)  # evita agendamento duplicado ao rodar de novo
        caminho_plist(label).write_text(texto)
        resultado[label] = carregar(label)
    return resultado


def desinstalar():
    print("\n🧹 Desativando a publicação automática no Instagram\n")
    for label, _script in AGENTS:
        descarregar(label)
        plist = caminho_plist(label)
        if plist.exists():
            try:
                plist.unlink()
                print("   ✅ Agendamento removido: %s" % label)
            except Exception as e:
                print("   ⚠️  Não consegui remover %s (%s)" % (plist, e))
        else:
            print("   • %s já não estava agendado" % label)
    marcar_config(IG_ENV.exists(), False)
    print("\n📌 A sua credencial NÃO foi apagada. Ela continua em:")
    print("   %s" % IG_ENV)
    print("   Se quiser encerrar de vez, apague esse arquivo e revogue o acesso")
    print("   do App em https://developers.facebook.com/apps/")
    print("\n✅ Pronto. A fila e os vídeos continuam onde estavam.\n")
    return 0


# ── etapas do fluxo ───────────────────────────────────────────────────────
def explicar():
    print("\n🎬 Bônus opcional — Publicação Automática no Instagram")
    print("   (fora das 8 etapas do Setup 7 — pular não afeta nada)\n")
    print("   O que isso faz: você coloca os vídeos numa fila, escreve a legenda")
    print("   de cada um, e o seu Mac publica 1 Reel por dia sozinho, no horário")
    print("   que você escolher — pela API oficial do Instagram.\n")
    print("   O que você precisa ter:")
    print("     1. Conta do Instagram Business ou Creator")
    print("     2. Um App criado no Meta for Developers")
    print("     3. Um token de longa duração do Instagram")
    print("     4. Um lugar público na internet pra hospedar o vídeo")
    print("     5. O Mac ligado no horário do post\n")
    print("   Passo a passo com telas: %s\n" % DOC)


def checar_tipo_de_conta():
    print("Primeiro, o pré-requisito que mais trava gente:\n")
    resp = prompt("   Sua conta do Instagram é Business ou Creator?", "sim")
    if sim(resp):
        return True
    print("\n   Sem problema — a conversão é grátis e leva 1 minuto, no próprio app:")
    print("     Instagram > Menu > Configurações > Tipo de conta e ferramentas")
    print("     > Mudar para conta profissional > escolha Criador de conteúdo ou Empresa")
    print("\n   Depois de converter, é só me pedir pra rodar esta configuração de novo.")
    seguir = prompt("   Quer seguir mesmo assim e configurar o resto agora?", "nao")
    return sim(seguir)


def avisar_plataforma():
    if sys.platform == "darwin":
        return True
    print("\n⚠️  Este computador não é um Mac.")
    print("   Nesta versão, o AGENDAMENTO automático só existe para macOS.")
    print("   O resto funciona normalmente: dá pra configurar a credencial e")
    print("   publicar quando quiser, rodando a publicação na hora.\n")
    return False


def descobrir_id(ig, token):
    """Descobre o IG_USER_ID a partir do token, quando o aluno não achou na tela.

    O guia promete isso no passo 3.6. Sem esta função, a promessa obrigaria o
    Claude a improvisar um comando com o token na linha de comando — que é
    exatamente o que a Regra 8 proíbe.
    """
    print("\n🔎 Você não passou o ID — vou tentar descobrir pelo próprio token...")
    try:
        user_id, username = ig.resolve_user_id(token)
    except Exception as e:
        print("   Não consegui: %s" % ig.safe_error_repr(e))
        print("   Sem problema — o ID aparece na tela de configuração do")
        print("   Instagram dentro do App, no Meta for Developers (%s, passo 3.6)." % DOC)
        return ""
    if username:
        print("   ✅ Achei: conta @%s (ID %s)" % (username, user_id))
    else:
        print("   ✅ Achei o ID: %s" % user_id)
    return user_id


def coletar_credencial(ig, env_atual):
    ig_user_id = env_atual.get("IG_USER_ID", "")
    token = env_atual.get("IG_ACCESS_TOKEN", "")

    if ig_user_id and token:
        print("\n🔎 Já existe uma configuração do Instagram nesta máquina:")
        print("   IG_USER_ID    : %s" % ig_user_id)
        print("   Token         : %s" % mascara(token))
        if sim(prompt("   Quer continuar usando essa credencial?", "sim")):
            return ig_user_id, token
        print("   OK — vamos colocar uma credencial nova.")

    print("\n🔑 Agora preciso de 2 informações do Meta for Developers.")
    print("   Se você ainda não tem, o passo a passo está em %s" % DOC)
    print("   (para quem nunca mexeu nesse painel, o vídeo de apresentação do")
    print("    Setup de Tráfego Pago mostra como conectar a conta Meta e gerar token)\n")

    print("   Se você não achou o ID numérico, deixe em branco: eu descubro")
    print("   ele a partir do token.\n")

    novo_id = prompt("   Cole o IG_USER_ID (só números, ou deixe em branco)", ig_user_id)
    novo_token = prompt_secreto("   Cole o token de longa duração (ele não aparece na tela)")
    if not novo_token:
        novo_token = token
    if novo_token:
        print("   Token recebido: %s" % mascara(novo_token))

    novo_id = (novo_id or "").strip()
    novo_token = (novo_token or "").strip()
    if novo_token and not novo_id:
        novo_id = descobrir_id(ig, novo_token)
    return novo_id, novo_token


def validar(ig, ig_user_id, token):
    """Retorna (ok, username_ou_mensagem)."""
    print("\n🔐 Testando a credencial com o Instagram (só leitura, não publica nada)...")
    try:
        username = ig.validate_credentials(ig_user_id, token)
        return True, username
    except Exception as e:
        return False, ig.safe_error_repr(e)


def escolher_hospedagem(env_atual):
    print("\n📦 Onde o vídeo vai ficar hospedado?")
    print("   A API do Instagram não aceita arquivo do seu computador: o vídeo")
    print("   precisa estar numa URL pública (HTTPS, sem login).\n")
    print("   1) Bunny Storage — o script sobe o vídeo sozinho (automático).")
    print("      Custa poucos dólares por mês e pede cartão no cadastro.")
    print("   2) Manual — você hospeda onde quiser e cola a URL num arquivo .url")
    print("      ao lado do vídeo. Custo zero, mas você cola a URL de cada vídeo.\n")

    atual = (env_atual.get("IG_VIDEO_HOST_PROVIDER") or "bunny").lower()
    padrao = "1" if atual == "bunny" else "2"
    escolha = prompt("   Escolha 1 ou 2", padrao)
    if escolha.strip() == "2":
        return [("IG_VIDEO_HOST_PROVIDER", "manual")]

    print("\n   Dados do Bunny Storage (painel do Bunny > Storage > FTP & API Access):")
    zona = prompt("   Nome da Storage Zone", env_atual.get("BUNNY_STORAGE_ZONE", ""))
    host = prompt("   Hostname do storage (ex: storage.bunnycdn.com)",
                  env_atual.get("BUNNY_STORAGE_HOST", "storage.bunnycdn.com"))
    senha = prompt("   Senha/AccessKey da zona (não vou repetir na tela)",
                   env_atual.get("BUNNY_STORAGE_PASSWORD", ""))
    if senha:
        print("   Chave recebida: %s" % mascara(senha))
    pull = prompt("   Hostname da Pull Zone (ex: minha-zona.b-cdn.net)",
                  env_atual.get("BUNNY_PULL_HOST", ""))
    pasta = prompt("   Pasta dentro da zona", env_atual.get("BUNNY_FOLDER", "reels"))

    faltando = [n for n, v in (("Storage Zone", zona), ("Storage Host", host),
                               ("AccessKey", senha), ("Pull Host", pull)) if not v]
    if faltando:
        print("\n   ⚠️  Faltou: %s" % ", ".join(faltando))
        print("   Vou salvar assim mesmo; a publicação vai avisar exatamente o que")
        print("   está faltando quando você rodar. Dá pra completar depois.")

    return [
        ("IG_VIDEO_HOST_PROVIDER", "bunny"),
        ("BUNNY_STORAGE_ZONE", zona),
        ("BUNNY_STORAGE_HOST", host),
        ("BUNNY_STORAGE_PASSWORD", senha),
        ("BUNNY_PULL_HOST", pull),
        ("BUNNY_FOLDER", pasta or "reels"),
    ]


def preparar_fila(provider):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    print("\n📁 Fila criada em: %s" % QUEUE_DIR)
    print("   Como usar — para cada Reel, 2 arquivos com o MESMO nome:")
    print("     meu-reel.mp4   o vídeo")
    print("     meu-reel.txt   a legenda do post (obrigatório)")
    if provider == "manual":
        print("     meu-reel.url   a URL pública HTTPS do vídeo (modo manual)")
    print("\n   Sem o arquivo .txt o vídeo é PULADO de propósito — eu nunca")
    print("   escrevo legenda no seu lugar.")


def rodar_dry_run():
    print("\n🧪 Teste sem publicar (--dry-run):\n")
    sys.stdout.flush()  # o teste roda em outro processo: mantém a ordem na tela
    r = subprocess.run([sys.executable, str(PUBLISHER), "--dry-run"])
    if r.returncode != 0:
        print("\n⚠️  O teste terminou com aviso (código %s)." % r.returncode)
        print("   Isso costuma ser só configuração faltando — a mensagem acima diz o quê.")
    return r.returncode == 0


def agendar():
    print("\n⏰ Agendamento automático")
    print("   Vou criar 2 rotinas no seu Mac:")
    print("     • publicar 1 Reel por dia, no horário que você escolher")
    print("     • renovar o token do Instagram 1x por semana (segunda, 09:30)")
    print("   O Mac precisa estar ligado nesse horário.\n")

    # Pergunta irreversível: só ativa com um "sim" digitado (default = não).
    if not confirmar("   Quer ativar o agendamento automático agora?"):
        print("\n   Sem problema. Você pode publicar quando quiser, e ativar o")
        print("   agendamento depois — é só me pedir.")
        return False

    hora = prompt("   Que horas publicar? (0-23)", "10")
    minuto = prompt("   Em que minuto? (0-59)", "30")
    try:
        hora = max(0, min(23, int(hora)))
        minuto = max(0, min(59, int(minuto)))
    except ValueError:
        print("   Valor inválido — vou usar 10:30.")
        hora, minuto = 10, 30

    resultado = renderizar_plists(hora, minuto)
    label_pub, label_token = AGENTS[0][0], AGENTS[1][0]
    pub_ok = resultado.get(label_pub, False)
    token_ok = resultado.get(label_token, False)

    if pub_ok and token_ok:
        print("\n✅ Agendado: 1 Reel por dia às %02d:%02d" % (hora, minuto))
        print("   Renovação do token: toda segunda, 09:30")
        print("   Conferir quando quiser: launchctl list | grep socialmediaagent")
        return True

    print("\n⚠️  O agendamento ficou pela metade. Situação real:")
    print("   • publicação diária : %s" % ("ATIVA às %02d:%02d" % (hora, minuto)
                                           if pub_ok else "não ativada"))
    print("   • renovação do token: %s" % ("ativa" if token_ok else "NÃO ativada"))

    if pub_ok and not token_ok:
        print("\n   🚨 Atenção: a publicação VAI acontecer todo dia, mas o token")
        print("   não será renovado sozinho — ele expira em 60 dias e aí a")
        print("   publicação para sem aviso.")
        if confirmar("   Quer que eu desative a publicação diária por segurança?"):
            descarregar(label_pub)
            print("   ✅ Publicação diária desativada. Nada será postado sozinho.")
            return False
        print("   OK — deixei a publicação ativa. Me peça pra renovar o token")
        print("   antes de 60 dias, ou rode esta configuração de novo.")
    return pub_ok or token_ok


# ── main ──────────────────────────────────────────────────────────────────
def analisar_argumentos():
    # allow_abbrev=False de propósito: sem isso um `--uninstal` (com um L só)
    # casaria por prefixo e DESINSTALARIA o agendamento sem querer.
    parser = argparse.ArgumentParser(
        prog="setup_publicacao_ig.py", allow_abbrev=False,
        description="Configura (ou desativa) a publicação automática de 1 Reel "
                    "por dia no Instagram. Bônus opcional do Setup 7.")
    parser.add_argument("--uninstall", action="store_true",
                        help="remove os 2 agendamentos (não apaga a sua credencial)")
    return parser.parse_args()


def executar():
    args = analisar_argumentos()
    if args.uninstall:
        return desinstalar()

    explicar()

    if not checar_tipo_de_conta():
        print("\n⏸  Tudo bem — paramos por aqui. Nada foi alterado.")
        print("   Quando a conta estiver como Business ou Creator, é só me chamar.\n")
        return 0

    pode_agendar = avisar_plataforma()

    try:
        import ig_common as ig
    except Exception as e:
        print("\n❌ Não encontrei os arquivos da automação em %s" % AUTOMATIONS)
        print("   Detalhe: %s" % e)
        print("   Confira se o repositório do Setup 7 está completo.\n")
        return 1

    env_atual = ler_env()
    ig_user_id, token = coletar_credencial(ig, env_atual)

    if not ig_user_id or not token:
        print("\n⚠️  Sem o IG_USER_ID e o token eu não consigo continuar.")
        print("   O passo a passo pra gerar os dois está em %s" % DOC)
        print("   Quando tiver, é só me pedir pra rodar isto de novo.\n")
        return 2

    ok, resultado = validar(ig, ig_user_id, token)

    # O carimbo tem que acompanhar o TOKEN. Preservar o antigo com um token novo
    # faria o arquivo mentir sobre a idade dele.
    token_mudou = token != env_atual.get("IG_ACCESS_TOKEN", "")
    carimbo = env_atual.get("IG_TOKEN_GENERATED_AT")
    if token_mudou or not carimbo:
        carimbo = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    pares = [("IG_USER_ID", ig_user_id),
             ("IG_ACCESS_TOKEN", token),
             ("IG_TOKEN_GENERATED_AT", carimbo)]

    if not ok:
        print("\n❌ O Instagram não aceitou essa credencial.")
        print("   Motivo: %s" % resultado)
        print("\n   Confira, na ordem:")
        print("     • a conta é Business ou Creator?")
        print("     • o token é do Instagram (não é o token de anúncios do Meta)?")
        print("     • o App tem as permissões instagram_business_basic e")
        print("       instagram_business_content_publish?")
        print("     • o token não passou de 60 dias?")
        print("   Detalhes de cada erro: %s" % DOC)

        # Um agendamento vivo contra credencial que não funciona é falha diária
        # invisível. Desligamos antes de qualquer outra coisa.
        desligou = False
        for label, _script in AGENTS:
            if caminho_plist(label).exists():
                descarregar(label)
                try:
                    caminho_plist(label).unlink()
                except Exception:
                    pass
                desligou = True
        if desligou:
            print("\n   ⏸  Desativei o agendamento automático: não faz sentido")
            print("   tentar publicar todo dia com uma credencial recusada.")

        token_antigo = env_atual.get("IG_ACCESS_TOKEN", "")
        if token_antigo and token_mudou:
            # NÃO sobrescrevemos um token que talvez ainda funcione por um que
            # acabou de ser recusado — e guardamos cópia do arquivo de qualquer jeito.
            copia = backup_env()
            print("\n   📌 Mantive o token anterior no arquivo (o novo foi recusado).")
            if copia:
                print("   Cópia de segurança: %s" % copia.name)
            pares = [("IG_USER_ID", env_atual.get("IG_USER_ID") or ig_user_id),
                     ("IG_ACCESS_TOKEN", token_antigo),
                     ("IG_TOKEN_GENERATED_AT",
                      env_atual.get("IG_TOKEN_GENERATED_AT") or carimbo)]
        else:
            backup_env()

        pares.extend(escolher_hospedagem(env_atual))
        gravar_env(pares, env_atual)
        marcar_config(True, False)
        print("\n📌 Salvei o que você já preencheu, pra você não recomeçar do zero.")
        print("   NÃO agendei nada — não faz sentido agendar com credencial que")
        print("   não funciona. Corrija e me peça pra rodar de novo.\n")
        return 3

    print("\n✅ Credencial válida. Conta conectada: @%s" % resultado)
    if not confirmar("   Essa é a sua conta do Instagram?"):
        print("\n   Então o token é de outra conta ligada ao mesmo App.")
        print("   Gere o token com a conta certa selecionada e me chame de novo.")
        print("   Nada foi agendado. Passo a passo: %s\n" % DOC)
        return 3

    pares_hosting = escolher_hospedagem(env_atual)
    provider = dict(pares_hosting).get("IG_VIDEO_HOST_PROVIDER", "bunny")
    pares.extend(pares_hosting)
    pares.append(("IG_SHARE_TO_FEED", env_atual.get("IG_SHARE_TO_FEED", "true")))
    backup_env()
    gravar_env(pares, env_atual)

    preparar_fila(provider)
    dry_ok = rodar_dry_run()

    agendado = False
    if pode_agendar:
        # O teste sem publicar e o unico sinal de que a rotina diaria vai
        # funcionar. Se ele falhou, agendar assim mesmo instala um robo que
        # erra todo dia em silencio — entao aqui a pergunta muda de tom e o
        # default deixa de ser seguir em frente.
        if dry_ok:
            agendado = agendar()
        else:
            print("\n⚠️  O teste sem publicar não passou.")
            print("   Se eu agendar agora, a rotina vai falhar todo dia sem você ver.")
            print("   O normal aqui é corrigir o que a mensagem acima apontou e me")
            print("   pedir pra ativar o agendamento depois.")
            if confirmar("   Mesmo assim, quer agendar agora?"):
                agendado = agendar()
            else:
                print("\n   Beleza — nada agendado. Sua credencial já está salva:")
                print("   quando quiser, me peça 'ativa o agendamento do Instagram'.")
    else:
        print("\n⏭  Agendamento pulado (só macOS nesta versão).")

    marcar_config(True, agendado)

    print("\n" + "=" * 62)
    print("✅ Publicação automática no Instagram configurada")
    print("   Conta        : @%s" % resultado)
    print("   Fila         : %s" % QUEUE_DIR)
    print("   Agendamento  : %s" % ("ativo" if agendado else "não ativado"))
    print("   Guia         : %s" % DOC)
    print("=" * 62)
    print("\nPróximo passo: coloque um .mp4 e um .txt com a legenda na fila.")
    print("Quer testar antes? me peça: 'testa a publicação sem publicar'.\n")
    return 0


def main():
    try:
        return executar()
    except KeyboardInterrupt:
        print("\n\nCancelado. Nada ficou pela metade — pode rodar de novo quando quiser.\n")
        return 130
    except Exception as e:
        # Rede de segurança: o aluno nunca deve ver um traceback do Python.
        print("\n❌ Algo deu errado na configuração.")
        print("   Detalhe: %s" % erro_seguro(e))
        print("   Nada foi agendado. Guia: %s\n" % DOC)
        return 1


if __name__ == "__main__":
    sys.exit(main())
