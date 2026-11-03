#!/usr/bin/env python3
"""
Setup 7 — Etapa 0: Diagnóstico e estrutura de pastas.
Valida as ferramentas (Python, gh, ffmpeg, Chrome), garante config.json mínimo (sem exigir setup anterior), checa Codex/ChatGPT CLI
(image2 → gerar-imagem), Higgsfield MCP (opcional, imagens fallback), cria diretórios.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
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
    print("    Instalar (opcional): npm install -g @openai/codex")
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


class ConfigBackupError(OSError):
    """Nao foi possivel guardar copia de seguranca do config; o original NAO foi tocado."""


def backup_config_copy(path):
    """Copia (copy2) o config para <nome>.bak-<AAAAmmdd-HHMMSS>[-N], sem sobrescrever backup existente.

    Confere que o destino existe com o mesmo tamanho. Em falha, o original fica intacto
    e levanta ConfigBackupError (so entao o chamador pode recriar o config).
    """
    path = Path(path)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = None
    try:
        n = 0
        while backup is None:
            candidate = path.with_name("%s.bak-%s%s" % (path.name, stamp, "-%d" % n if n else ""))
            try:
                # O_EXCL: a criação é atômica; se outro processo pegou o nome, tenta o próximo sufixo.
                fd = os.open(str(candidate), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                n += 1
                continue
            backup = candidate
            with os.fdopen(fd, "wb") as dst, open(str(path), "rb") as src:
                shutil.copyfileobj(src, dst)
            os.chmod(str(backup), 0o600)  # backup nunca herda permissao aberta do original
        if not backup.is_file() or backup.stat().st_size != path.stat().st_size:
            raise OSError("copia de seguranca incompleta")
    except OSError as e:
        try:
            if backup is not None and backup.is_file():
                backup.unlink()
        except OSError:
            pass
        msg = (f"Não consegui salvar uma cópia de segurança de {path}: {e}. "
               "Verifique a permissão da pasta e rode de novo.")
        print(f"❌ {msg}")
        raise ConfigBackupError(msg) from e
    return backup



def write_config_atomic(cfg, path=None):
    """Grava o config.json por arquivo temporario 0600 no mesmo diretorio + os.replace (nunca deixa truncado)."""
    destino = os.path.realpath(str(path or CONFIG))
    tmp = "%s.tmp-%d" % (destino, os.getpid())
    try:
        try:
            os.unlink(tmp)  # sobra de execucao interrompida
        except FileNotFoundError:
            pass
        with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as f:
            f.write(json.dumps(cfg, indent=2) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, destino)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

def parse_phase(value):
    """Interpreta phase_completed de forma tolerante: 5, 5.0, "5", "week5", "semana 5", "phase5". Invalido = 0."""
    if isinstance(value, bool):
        return 0
    try:
        number = float(value)
    except OverflowError:
        number = float("inf") if value > 0 else 0.0  # inteiro gigante: maior que qualquer fase, nunca sobrescreve
    except (TypeError, ValueError):
        achou = re.search(r"\d+(?:\.\d+)?", str(value))
        number = float(achou.group()) if achou else 0
    if number != number or number == float("-inf"):
        return 0
    return number


def check_prior_setup(escrever=True):
    """Garante um config.json utilizavel. Este setup nao exige nenhum setup anterior.

    - Ausente: cria o minimo ({"phase_completed": 0}).
    - Corrompido: guarda copia em config.json.bak-<timestamp> e recria o minimo.
    - Valido (instalacao anterior): aproveita como esta, sem alterar.
    Nunca bloqueia nem pede para instalar outro setup.
    Com escrever=False (check_prerequisites.py) so informa, sem tocar no disco.
    """
    if not escrever:
        if not CONFIG.exists():
            print("ℹ️  Primeira instalação — a Etapa 0 cria o config.json mínimo")
        else:
            print("✅ config.json encontrado — a Etapa 0 aproveita o que for válido")
        return True
    try:
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        if not CONFIG.exists():
            try:
                fd = os.open(str(CONFIG), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                fd = None  # criado em paralelo por outra execucao: cai na leitura abaixo
            if fd is not None:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(json.dumps({"phase_completed": 0}, indent=2) + "\n")
                print("✅ Primeira instalação — config.json mínimo criado")
                return True
        try:
            cfg = json.loads(CONFIG.read_text())
            if not isinstance(cfg, dict):
                raise ValueError("config.json não é um objeto JSON")
        except Exception as e:
            backup = backup_config_copy(CONFIG)  # ConfigBackupError: original fica intacto
            write_config_atomic({"phase_completed": 0})
            print(f"⚠️  config.json inválido ({e}) — cópia guardada em {backup.name}; mínimo recriado")
            return True
    except ConfigBackupError:
        return False  # mensagem ja impressa; config original intacto
    except OSError as e:
        print(f"❌ Não consegui preparar o config.json ({e}). Verifique a permissão da pasta {CONFIG.parent} e rode de novo.")
        return False
    print(f"✅ Instalação anterior encontrada (phase_completed={cfg.get('phase_completed', 0)}) — aproveitando o que for válido")
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

    if not checks[-1]:  # config.json: so falha por permissao/disco (nunca por setup anterior)
        print("\n❌ Não foi possível preparar o config.json. Resolva a permissão e rode novamente.")
        sys.exit(1)

    create_dirs()
    show_plan()
    print("\n✅ Etapa 0 concluída. Pronto para a Etapa 1 (Identidade da Marca).")


if __name__ == "__main__":
    main()
