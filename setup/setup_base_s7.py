#!/usr/bin/env python3
"""
Setup 7 — Etapa 0: Diagnóstico e estrutura de pastas.
Valida pré-requisitos (Python, gh, ffmpeg), checa Higgsfield MCP, cria diretórios.
"""
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

OPERACAO = Path.home() / ".operacao-ia"
CONFIG = OPERACAO / "config" / "config.json"

REQUIRED_DIRS = [
    OPERACAO / "config",
    OPERACAO / "data" / "social-media",
    OPERACAO / "data" / "social-media" / "output" / "reels",
    OPERACAO / "data" / "social-media" / "output" / "carrosseis",
    OPERACAO / "data" / "social-media" / "output" / "thumbs",
    OPERACAO / "data" / "social-media" / "output" / "stories",
    OPERACAO / "data" / "social-media" / "output" / "repurpose",
    OPERACAO / "data" / "social-media" / "output" / "demo",
    OPERACAO / "tools",
    OPERACAO / "logs",
]

ETAPAS = [
    "E0  Boas-vindas + Diagnóstico",
    "E1  Identidade da Marca",
    "E2  Design System",
    "E3  Instalar video-use (Whisper local)",
    "E4  Instalar 6 Skills",
    "E5  Dashboard Local",
    "E6  Demo de Geração (carrossel + reel)",
    "E7  Finalização",
]


def check_python():
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ requerido. Você tem {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_gh():
    if shutil.which("gh"):
        print("✅ gh CLI instalado")
        return True
    print("❌ gh CLI não encontrado. Instale com: brew install gh")
    return False


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        print("✅ ffmpeg instalado")
        return True
    print("⚠️  ffmpeg não encontrado. Instale com: brew install ffmpeg")
    print("    (necessário para repurpose-conteudo)")
    return True  # não bloqueia — só repurpose precisa


def check_claude_cli():
    if shutil.which("claude"):
        print("✅ Claude Code CLI instalado")
        return True
    print("❌ Claude Code CLI não encontrado. Instale antes de prosseguir.")
    return False


def check_higgsfield_mcp():
    """Verifica se higgsfield aparece em `claude mcp list`."""
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True, text=True, timeout=15,
        )
        out = (result.stdout + result.stderr).lower()
        if "higgsfield" in out and "connected" in out:
            print("✅ Higgsfield MCP conectado")
            return True
        if "higgsfield" in out:
            print("⚠️  Higgsfield MCP listado mas não conectado — faça login antes de prosseguir")
            return False
        print("❌ Higgsfield MCP não conectado")
        print("    Conecte com:")
        print("    claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp")
        return False
    except Exception as e:
        print(f"⚠️  Não foi possível verificar MCPs: {e}")
        return True  # não bloqueia — aluno pode estar offline temporário


def check_prior_setup():
    if not CONFIG.exists():
        print(f"⚠️  Config base não encontrado: {CONFIG}")
        print("    Recomendado concluir Setups 1-6 antes do Setup 7, mas vou prosseguir.")
        return True
    try:
        cfg = json.loads(CONFIG.read_text())
    except Exception as e:
        print(f"⚠️  Config corrompido: {e}")
        return True
    phase = cfg.get("phase_completed", 0)
    if phase < 6:
        print(f"⚠️  Setups anteriores não concluídos (phase_completed={phase}).")
        print("    Recomendado concluir Setup 6 (Tráfego Pago) antes, mas vou prosseguir.")
    else:
        print(f"✅ Setup 6 concluído (phase_completed={phase})")
    return True


def create_dirs():
    for d in REQUIRED_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ Estrutura criada em {OPERACAO}/data/social-media/")


def show_plan():
    print("\n" + "=" * 60)
    print("PLANO DAS 8 ETAPAS — Setup 7 Social Media Agent")
    print("=" * 60)
    for e in ETAPAS:
        print(f"  {e}")
    print("=" * 60)


def main():
    print(f"\n🔍 Diagnóstico inicial — {platform.system()} {platform.release()}\n")

    checks = [
        check_python(),
        check_gh(),
        check_claude_cli(),
        check_ffmpeg(),
        check_higgsfield_mcp(),
        check_prior_setup(),
    ]

    blocking = checks[:3]  # python, gh, claude são bloqueantes
    if not all(blocking):
        print("\n❌ Diagnóstico falhou em itens bloqueantes. Resolva e rode novamente.")
        sys.exit(1)

    create_dirs()
    show_plan()
    print("\n✅ Etapa 0 concluída. Pronto para a Etapa 1 (Identidade da Marca).")


if __name__ == "__main__":
    main()
