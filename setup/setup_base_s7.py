#!/usr/bin/env python3
"""
Setup 7 — Etapa 0: Diagnóstico e estrutura de pastas.
Valida pré-requisitos (Python, gh, ffmpeg, Chrome), checa Codex/ChatGPT CLI
(image2 → gerar-imagem), Higgsfield MCP (opcional, imagens fallback), cria diretórios.
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
    "E3  Setup de Transcrição (ElevenLabs + Whisper fallback)",
    "E4  Instalar 8 Skills",
    "E5  Dashboard Local",
    "E6  Demo de Geração (carrossel + reel animado MP4)",
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
    """Verifica higgsfield MCP. NÃO bloqueia (geração de vídeo agora é via gerar-video-mp4,
    e imagens preferem gpt-image-2 via Codex CLI — Higgsfield vira fallback opcional)."""
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True, text=True, timeout=15,
        )
        out = (result.stdout + result.stderr).lower()
        if "higgsfield" in out and "connected" in out:
            print("✅ Higgsfield MCP conectado (fallback de imagens disponível)")
        elif "higgsfield" in out:
            print("⚠️  Higgsfield MCP listado mas não conectado — sem fallback de imagens AI")
        else:
            print("ℹ️  Higgsfield MCP não conectado (opcional — só usado como fallback de imagens)")
            print("    Para conectar (opcional): claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp")
    except Exception as e:
        print(f"⚠️  Não foi possível verificar MCPs: {e}")
    return True  # NUNCA bloqueia


def check_codex_or_chatgpt_cli():
    """Image gen preferida usa gpt-image-2 via Codex CLI (login ChatGPT). Não bloqueia."""
    if shutil.which("codex"):
        try:
            result = subprocess.run(
                ["codex", "login", "status"], capture_output=True, text=True, timeout=10
            )
            out = (result.stdout + result.stderr).lower()
            if "logged in" in out or "chatgpt" in out:
                print("✅ Codex CLI logado em ChatGPT (gpt-image-2 disponível para imagens)")
                return True
            print("⚠️  Codex CLI instalado mas não logado em ChatGPT")
            print("    Para ativar gpt-image-2: codex login")
            return True
        except Exception:
            print("⚠️  Codex CLI presente mas erro ao consultar status — pode estar disponível")
            return True
    print("ℹ️  Codex CLI não encontrado (opcional — usado pra gpt-image-2)")
    print("    Instalar (opcional): npm install -g @openai/codex   ou   pip install openai-codex")
    print("    Sem Codex, gerar-imagem cai automaticamente em Gemini Nano Banana (chave Gemini opcional).")
    return True  # nunca bloqueia


def check_chrome():
    """gerar-video-mp4 usa Chrome headless via puppeteer. Não bloqueia."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for path in candidates:
        if Path(path).exists():
            print("✅ Chrome/Chromium instalado (gerar-video-mp4 OK)")
            return True
    if shutil.which("google-chrome") or shutil.which("chromium"):
        print("✅ Chrome no PATH (gerar-video-mp4 OK)")
        return True
    print("⚠️  Chrome/Chromium não encontrado — necessário para gerar-video-mp4 (Reels).")
    print("    Instale Chrome (https://www.google.com/chrome/) antes da Etapa 6.")
    return True  # não bloqueia — só Reels precisam


def check_bun():
    """gerar-video-mp4 usa puppeteer-core via Bun. Não bloqueia."""
    if shutil.which("bun"):
        print("✅ Bun instalado (puppeteer/gerar-video-mp4 OK)")
        return True
    print("⚠️  Bun não encontrado — necessário para gerar-video-mp4 rodar puppeteer-core.")
    print("    Instale com: brew install bun  (antes da Etapa 6, só Reels precisam)")
    return True  # não bloqueia — só Reels precisam


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
        check_chrome(),
        check_bun(),
        check_codex_or_chatgpt_cli(),
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
