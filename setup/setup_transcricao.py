#!/usr/bin/env python3
"""
Setup 7 — Etapa 3: Setup de Transcrição (ElevenLabs preferred + Whisper fallback).

Fluxo:
1. Pergunta ao aluno se ele já tem (ou quer pegar) uma API key da ElevenLabs.
   - Free tier generoso (~10h/mês de speech-to-text via Scribe v1).
   - Cadastro gratuito em https://elevenlabs.io/app/sign-up
   - Chave em https://elevenlabs.io/app/settings/api-keys
2. Se sim → salva em ~/.operacao-ia/config/elevenlabs.env + smoke test (HTTP HEAD).
3. Sempre instala Whisper local (faster-whisper via video-use) como fallback —
   funciona offline e é grátis, mas é ~3-5x mais lento que ElevenLabs Scribe.

A skill `repurpose-conteudo` lê elevenlabs.env primeiro; se falhar (chave inválida,
limite atingido, sem internet), cai automaticamente no Whisper local.
"""
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()
OPERACAO = HOME / ".operacao-ia"
TOOLS = OPERACAO / "tools"
CONFIG = OPERACAO / "config"
VU_DIR = TOOLS / "video-use"
ELEVEN_ENV = CONFIG / "elevenlabs.env"
REPO = "https://github.com/browser-use/video-use"


def run(cmd, cwd=None, check=True):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    if check and result.returncode != 0:
        print(f"❌ Comando falhou: {' '.join(cmd)}")
        sys.exit(1)
    return result.returncode


def prompt(msg, default=""):
    suffix = f" [{default}]" if default else ""
    try:
        ans = input(f"{msg}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return default
    return ans or default


def ler_chave_existente():
    if not ELEVEN_ENV.exists():
        return None
    try:
        for linha in ELEVEN_ENV.read_text().splitlines():
            linha = linha.strip()
            if linha.startswith("ELEVENLABS_API_KEY="):
                v = linha.split("=", 1)[1].strip().strip('"').strip("'")
                if v and v != "SUA_CHAVE_AQUI":
                    return v
    except Exception:
        pass
    return None


def validar_chave(api_key):
    """Bate em GET /v1/user — se 200, chave válida."""
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user",
        headers={"xi-api-key": api_key, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False
        print(f"⚠️  ElevenLabs respondeu {e.code} — tratando como inválida.")
        return False
    except Exception as e:
        print(f"⚠️  Não foi possível validar online ({e}). Chave salva sem validação.")
        return True  # rede offline: aceita


def remover_chave_antiga():
    """Apaga o arquivo elevenlabs.env se existir — chamado quando o aluno
    decide não usar mais a chave existente."""
    if ELEVEN_ENV.exists():
        try:
            ELEVEN_ENV.unlink()
            print(f"🗑️  Chave antiga removida de {ELEVEN_ENV}")
        except Exception as e:
            print(f"⚠️  Não foi possível remover {ELEVEN_ENV}: {e}")


def setup_elevenlabs():
    print("\n🎙️  Transcrição — Provedor preferencial: ElevenLabs Scribe")
    print(
        "   • Free tier: minutos incluídos variam por plano (ver pricing oficial em https://elevenlabs.io/pricing/api)\n"
        "   • Velocidade: ~5-10x mais rápido que Whisper local\n"
        "   • Cadastro grátis: https://elevenlabs.io/app/sign-up\n"
        "   • Chave em:     https://elevenlabs.io/app/settings/api-keys\n"
        "   • Se preferir não usar, o Whisper local (offline) cobre tudo.\n"
    )

    existente = ler_chave_existente()
    if existente:
        print(f"✅ Já existe ELEVENLABS_API_KEY em {ELEVEN_ENV}")
        resp = prompt("   Reusar essa chave?", "sim").lower()
        if resp.startswith("s"):
            print("   OK — mantendo chave existente.")
            return True
        # Aluno rejeitou reuso → remove antes de seguir, senão skill ainda
        # vai tentar ElevenLabs com chave antiga.
        remover_chave_antiga()

    resp = prompt("Tem API key da ElevenLabs pra colar agora?", "nao").lower()
    if not resp.startswith("s"):
        print("⏭  Pulando ElevenLabs — Whisper local será usado como provedor único.")
        print(f"   Pra ativar depois, basta criar {ELEVEN_ENV} com:")
        print("   ELEVENLABS_API_KEY=xi-xxxxxxxxxxxxxxxxxxxx")
        return False

    chave = prompt("Cole a chave (começa com 'sk_' ou 'xi-')", "").strip()
    if not chave or chave == "SUA_CHAVE_AQUI":
        print("⏭  Nada colado — pulando ElevenLabs.")
        return False

    print("🔐 Validando chave...")
    if not validar_chave(chave):
        print("❌ Chave rejeitada pelo ElevenLabs (401/403). Verifique e rode esta etapa de novo.")
        return False

    CONFIG.mkdir(parents=True, exist_ok=True)
    ELEVEN_ENV.write_text(f"ELEVENLABS_API_KEY={chave}\n")
    try:
        ELEVEN_ENV.chmod(0o600)
    except Exception:
        pass
    print(f"✅ Chave salva em {ELEVEN_ENV} (chmod 600)")
    return True


def clone_or_pull():
    TOOLS.mkdir(parents=True, exist_ok=True)
    if VU_DIR.exists() and (VU_DIR / ".git").exists():
        print(f"✅ video-use já clonado em {VU_DIR} — atualizando...")
        run(["git", "-C", str(VU_DIR), "fetch", "--quiet"])
        run(["git", "-C", str(VU_DIR), "pull", "--quiet", "--ff-only"], check=False)
        return
    if VU_DIR.exists():
        print(f"⚠️  {VU_DIR} existe sem .git — removendo para clonar limpo")
        shutil.rmtree(VU_DIR)
    print(f"📥 Clonando video-use em {VU_DIR}...")
    run(["git", "clone", "--depth=1", REPO, str(VU_DIR)])


def setup_venv():
    venv = VU_DIR / ".venv"
    if venv.exists():
        print(f"✅ venv já existe em {venv}")
    else:
        print("🐍 Criando venv...")
        run([sys.executable, "-m", "venv", str(venv)])

    pip = venv / "bin" / "pip"
    if not pip.exists():
        print(f"❌ pip não encontrado em {pip}")
        sys.exit(1)

    print("📦 Instalando dependências (faster-whisper baixa modelo no primeiro uso, ~500MB)...")
    run([str(pip), "install", "-q", "-e", str(VU_DIR)])


def smoke_test_whisper():
    """Retorna True se faster_whisper importa OK, False caso contrário."""
    py = VU_DIR / ".venv" / "bin" / "python"
    print("\n🧪 Smoke test Whisper (import faster-whisper)...")
    code = (
        "import faster_whisper, sys; "
        "print(f'faster_whisper {faster_whisper.__version__} OK')"
    )
    rc = run([str(py), "-c", code], check=False)
    if rc == 0:
        print("✅ Whisper local OK (fallback pronto)")
        return True
    print("⚠️  Smoke test Whisper falhou — repurpose pode não ter fallback")
    return False


def main():
    print("\n📹 Etapa 3 — Setup de Transcrição (ElevenLabs preferred + Whisper fallback)\n")
    if not shutil.which("git"):
        print("❌ git não encontrado")
        sys.exit(1)

    eleven_ok = setup_elevenlabs()

    print("\n📦 Agora instalando Whisper local como fallback (sempre funciona offline)...")
    clone_or_pull()
    setup_venv()
    whisper_ok = smoke_test_whisper()

    # Se nenhum dos dois funcionou, repurpose-conteudo vai quebrar em runtime.
    # Aborta aqui para o aluno descobrir agora, não às 23h.
    if not eleven_ok and not whisper_ok:
        print("\n❌ Nem ElevenLabs nem Whisper local estão prontos.")
        print("   A skill repurpose-conteudo NÃO vai funcionar até resolver isso.")
        print("   Opções:")
        print("   • Rodar esta etapa de novo e colar uma API key ElevenLabs válida")
        print("   • Investigar por que faster-whisper falhou (venv quebrado, deps ausentes)")
        print(f"     Logs do venv: {VU_DIR}/.venv")
        sys.exit(1)

    print("\n✅ Setup de transcrição concluído")
    print(f"   • ElevenLabs:    {'configurado' if eleven_ok else 'NÃO configurado'}")
    print(f"   • Whisper local: {'OK' if whisper_ok else 'FALHOU (sem fallback offline!)'}")
    if not whisper_ok and eleven_ok:
        print("   ⚠️  Sem fallback offline — repurpose só funciona com ElevenLabs disponível.")
    print("\nPronto para a Etapa 4 (instalar skills).")


if __name__ == "__main__":
    main()
