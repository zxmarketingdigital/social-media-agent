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

    print("=" * 70)
    print(">>> CLAUDE: NÃO gere nada ainda. Primeiro faça o BRIEFING com o aluno.")
    print("=" * 70)
    print()
    print("Esta etapa produz 2 peças (1 carrossel + 1 Reel). Antes de invocar as")
    print("skills, colete do aluno as decisões editoriais — sem isso a demo vira")
    print("um 'apresentando a marca' genérico que ele vai descartar.")
    print()
    print("PERGUNTAS DO BRIEFING (1-6 obrigatórias, 7 opcional — faça UMA POR VEZ):")
    print()
    print("  1) Objetivo da demo")
    print("     → 'O que essa demo precisa provar/comunicar pro seu público?'")
    print("        Ex: lançar novo produto · ensinar framework · gerar autoridade ·")
    print("            captar lead · educar mercado · prova social.")
    print()
    print("  2) Tema/ângulo específico do carrossel")
    print("     → 'Sobre o que você quer o carrossel? Pode ser um tópico do seu")
    print("        nicho, uma dor do seu público, ou um framework que você usa.'")
    print("        Ex: '5 erros que matam agência iniciante' (não 'apresentando ZX LAB')")
    print()
    print("  3) Tema/hook do Reel")
    print("     → 'O Reel pode ser o mesmo tema do carrossel (formato comprimido)")
    print("        ou um ângulo diferente. Qual você prefere?'")
    print()
    print("  4) Produto/serviço em foco (se houver)")
    print("     → 'Esta peça promove algum produto/serviço específico, ou é")
    print("        conteúdo de topo de funil sem oferta direta?'")
    print()
    print("  5) CTA preferido")
    print("     → 'Qual é o próximo passo que você quer que a pessoa tome?'")
    print("        Ex: 'salva e me segue' · 'comenta INFO' · 'link na bio' ·")
    print("            'agenda call' · 'baixa o material grátis'.")
    print()
    print("  6) Estilo de copy (escolher 1, ou sugerir baseado no tom da marca)")
    print(f"     → Tom atual da marca: '{tom}'. Pergunte se quer manter ou ajustar")
    print("        pra: didático passo-a-passo · storytelling pessoal · provocador")
    print("        com opinião forte · vendedor com benefícios · case real.")
    print()
    print("  7) Referências (opcional)")
    print("     → 'Tem algum perfil/criador que faz conteúdo parecido com o que")
    print("        você quer? Cola 1-3 nomes pra eu calibrar o ritmo.'")
    print()
    print("DEPOIS DAS RESPOSTAS:")
    print()
    print("  • Apresente o briefing consolidado (carrossel: tema/CTA/estilo +")
    print("    Reel: tema/hook/CTA/estilo) e PERGUNTE 'Pode gerar? (s/n/ajustar)'.")
    print("  • Só após 's', invoque as skills:")
    print("      1. gerar-carrossel  — 5 slides (capa · problema · 3 pontos · CTA)")
    print(f"         Output dir: {DEMO_DIR}/carrossel-<slug-do-tema>/")
    print("      2. criar-reel       — 30s animado MP4, plataforma Instagram, 9:16")
    print(f"         Output: {DEMO_DIR}/reel-<slug-do-tema>.mp4")
    print()
    print("  • Após cada geração, atualize gallery.json (data['items']) com")
    print("    {type, title, path, platform, created_at}.")
    print()
    print("REGRAS:")
    print("  • Use marca.json (nome, persona, público, tom) E DESIGN.md como contexto,")
    print("    mas NUNCA pule o briefing — as respostas do aluno definem a peça.")
    print("  • Se ele disser 'tanto faz / você escolhe', proponha 2-3 ângulos e")
    print("    deixe ele escolher 1 — não decida sozinho.")
    print("  • Se alguma geração falhar:")
    print("    - Mostre a mensagem técnica em linguagem clara")
    print("    - Carrossel falhou em todos providers → instrua codex login OU GEMINI_API_KEY")
    print("    - Reel falhou → cheque Chrome/ffmpeg na Etapa 0")
    print("    - Nunca pule silenciosamente")
    print()
    print("Quando ambas as gerações concluírem (e o aluno aprovar visualmente),")
    print("avance para a Etapa 7 (Finalização).")


if __name__ == "__main__":
    main()
