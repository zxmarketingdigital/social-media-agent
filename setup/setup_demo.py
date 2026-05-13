#!/usr/bin/env python3
"""
Setup 7 — Etapa 6: Demo de Geração.
Valida estado, checa providers disponíveis (gerar-imagem + gerar-video-mp4) e
imprime as instruções para o Claude invocar `gerar-carrossel` e `criar-reel`
usando marca.json + DESIGN.md.

Higgsfield NÃO entra como provider — gerar-imagem só implementa image2/gemini/imagen.
A geração padrão é:
- Imagens via gerar-imagem (gpt-image-2 → Gemini Nano Banana → Imagen 4)
- Vídeo via gerar-video-mp4 (Chrome headless + ffmpeg, 100% local)
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DATA = Path.home() / ".operacao-ia" / "data" / "social-media"
CFG = Path.home() / ".operacao-ia" / "config"
MARCA = CFG / "marca.json"
DESIGN = DATA / "DESIGN.md"
DEMO_DIR = DATA / "output" / "demo"


def has_codex_logged_in():
    if not shutil.which("codex"):
        return False
    try:
        r = subprocess.run(["codex", "login", "status"],
                           capture_output=True, text=True, timeout=10)
        out = (r.stdout + r.stderr).lower()
        return "logged in" in out or "chatgpt" in out
    except Exception:
        return False


def has_gemini_key():
    if os.environ.get("GEMINI_API_KEY"):
        return True
    for envf in CFG.glob("*.env"):
        try:
            if "GEMINI_API_KEY=" in envf.read_text():
                return True
        except Exception:
            pass
    return False


def has_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    return (any(Path(p).exists() for p in candidates)
            or shutil.which("google-chrome") is not None
            or shutil.which("chromium") is not None)


def main():
    if not MARCA.exists():
        print("❌ marca.json não encontrado. Conclua a Etapa 1 antes.")
        sys.exit(1)
    if not DESIGN.exists():
        print("❌ DESIGN.md não encontrado. Conclua a Etapa 2 antes.")
        sys.exit(1)

    # Higgsfield NÃO entra como provider válido aqui: a skill gerar-imagem
    # não implementa Higgsfield, então tê-lo conectado não desbloqueia o carrossel.
    providers_imagem = []
    if has_codex_logged_in():
        providers_imagem.append("gpt-image-2 (Codex/ChatGPT)")
    if has_gemini_key():
        providers_imagem.append("Gemini Nano Banana / Imagen 4")

    if not providers_imagem:
        print("❌ Nenhum provider de imagem disponível para o carrossel.")
        print("   Configure pelo menos um antes da demo:")
        print("   • codex login   (gpt-image-2, recomendado — usa assinatura ChatGPT Plus)")
        print("   • crie ~/.operacao-ia/config/gemini.env com GEMINI_API_KEY=...")
        print("     (chave grátis em https://aistudio.google.com/apikey)")
        sys.exit(1)

    if not has_chrome():
        print("⚠️  Chrome/Chromium não encontrado — o Reel pode falhar.")
        print("   Instale Chrome (https://www.google.com/chrome/) e rode novamente.")

    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    try:
        marca = json.loads(MARCA.read_text())
    except Exception as e:
        print(f"❌ marca.json inválido: {e}")
        sys.exit(1)

    nome = marca.get("nome", "")
    nicho = marca.get("nicho", "")
    publico = marca.get("publico", "")
    tom = marca.get("tom", "")

    print("\n🎬 Demo de Geração — Etapa 6\n")
    print(f"   Marca: {nome}")
    print(f"   Nicho: {nicho}")
    print(f"   Público: {publico}")
    print(f"   Tom: {tom}")
    print(f"   DESIGN.md: {DESIGN}")
    print(f"   Providers de imagem disponíveis: {', '.join(providers_imagem)}")
    print(f"   Output: {DEMO_DIR}\n")

    print(">>> CLAUDE: agora invoque as 2 skills abaixo, NESTA ORDEM, salvando em output/demo/")
    print()
    print("    1) Skill: gerar-carrossel  (usa gerar-imagem internamente)")
    print(f"       Prompt: '5 slides apresentando a marca {nome} para {publico} no nicho de {nicho}.")
    print(f"               Tom: {tom}. Estrutura: capa, problema, 3 pontos, CTA. Plataforma: Instagram.'")
    print(f"       Output dir: {DEMO_DIR}/carrossel-apresentacao/")
    print()
    print("    2) Skill: criar-reel  (usa gerar-video-mp4 internamente — HTML animado → MP4)")
    print(f"       Prompt: 'Reel 30 segundos animado apresentando {nome}.")
    print(f"               Hook: \"Você sabia que [insight do nicho {nicho}]?\".")
    print(f"               Corpo: 2 ideias-chave. CTA final: seguir o perfil. Tom: {tom}.")
    print("                Plataforma: Instagram, 9:16.'")
    print(f"       Output: {DEMO_DIR}/reel-apresentacao.mp4")
    print()
    print("    Após cada geração, atualize gallery.json adicionando o item criado.")
    print()
    print("    Se alguma geração falhar:")
    print("    - Mostre a mensagem técnica ao aluno em linguagem clara")
    print("    - Carrossel falhando em todos providers: instrua codex login OU GEMINI_API_KEY")
    print("    - Reel falhando: cheque Chrome/ffmpeg na Etapa 0")
    print("    - Não pule a etapa silenciosamente")
    print()
    print("Quando ambas as gerações concluírem, avance para a Etapa 7 (finalização).")


if __name__ == "__main__":
    main()
