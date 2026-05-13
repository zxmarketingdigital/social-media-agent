#!/usr/bin/env python3
"""
Setup 7 — Etapa 3: Instalar video-use.
Clona github.com/browser-use/video-use, cria venv, instala deps (faster-whisper).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path.home() / ".operacao-ia" / "tools"
VU_DIR = TOOLS / "video-use"
REPO = "https://github.com/browser-use/video-use"


def run(cmd, cwd=None, check=True):
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    if check and result.returncode != 0:
        print(f"❌ Comando falhou: {' '.join(cmd)}")
        sys.exit(1)
    return result.returncode


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


def smoke_test():
    """Testa import faster-whisper. Não baixa modelo (lazy) — só valida instalação."""
    py = VU_DIR / ".venv" / "bin" / "python"
    print("\n🧪 Smoke test (import faster-whisper)...")
    code = (
        "import faster_whisper, sys; "
        "print(f'faster_whisper {faster_whisper.__version__} OK')"
    )
    rc = run([str(py), "-c", code], check=False)
    if rc == 0:
        print("✅ Smoke test passou")
    else:
        print("⚠️  Smoke test falhou — repurpose pode não funcionar")


def main():
    print("\n📹 Instalando video-use (editor conversacional + Whisper local)\n")
    if not shutil.which("git"):
        print("❌ git não encontrado")
        sys.exit(1)
    clone_or_pull()
    setup_venv()
    smoke_test()
    print(f"\n✅ video-use pronto em {VU_DIR}")
    print("   A skill repurpose-conteudo usa essa instalação.")
    print("\nPronto para a Etapa 4 (instalar skills).")


if __name__ == "__main__":
    main()
