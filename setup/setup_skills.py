#!/usr/bin/env python3
"""
Setup 7 — Etapa 4: Instalar 8 Skills.

Copia 8 SKILL.md para ~/.claude/skills/.
Idempotente: skills idênticas são puladas; modificadas localmente recebem backup antes de atualizar.
"""
import datetime as dt
import filecmp
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_SRC = REPO_ROOT / "skills"
SKILLS_DST = Path.home() / ".claude" / "skills"

EXPECTED = [
    "agente-social-media",
    "criar-reel",
    "gerar-carrossel",
    "criar-thumbnail",
    "repurpose-conteudo",
    "gerar-copy-post",
    "gerar-imagem",
    "gerar-video-mp4",
]

SKILLS_DOCS = [
    {
        "slug": "agente-social-media",
        "icone": "🤖",
        "tipo": "Orquestrador",
        "o_que_faz": "Menu numérico que roteia entre todas as outras skills de social media. É o ponto de entrada quando o aluno não sabe qual usar.",
        "quando_usar": "Não sabe por onde começar, quer ver opções, ou prefere navegar por menu.",
        "trigger": "'agente social', 'menu social', 'criar conteudo'",
        "exemplo": "agente social",
    },
    {
        "slug": "criar-reel",
        "icone": "🎬",
        "tipo": "Especialista",
        "o_que_faz": "Gera Reel/Short/TikTok 9:16 animado em MP4. Claude escreve hook+corpo+CTA lendo marca.json/DESIGN.md, renderiza local via gerar-video-mp4 (Chrome headless + ffmpeg). Não depende de plano pago.",
        "quando_usar": "Quer publicar vídeo curto vertical (Instagram Reels, TikTok, YouTube Shorts).",
        "trigger": "'criar reel', 'novo reel', 'shorts', 'tiktok'",
        "exemplo": "criar reel sobre [tópico]",
    },
    {
        "slug": "gerar-carrossel",
        "icone": "🖼️",
        "tipo": "Especialista",
        "o_que_faz": "5-10 slides para Instagram (PNG) ou LinkedIn (PDF). Claude escreve copy de cada slide, gerar-imagem produz a arte (gpt-image-2 → Gemini → Imagen).",
        "quando_usar": "Quer um post educativo, framework, antes/depois, ou conteúdo carrossel.",
        "trigger": "'gerar carrossel', 'carrossel ig', 'carrossel linkedin', 'post educativo'",
        "exemplo": "gerar carrossel 7 slides sobre [tema] para linkedin",
    },
    {
        "slug": "criar-thumbnail",
        "icone": "🎯",
        "tipo": "Especialista",
        "o_que_faz": "3 variantes A/B/C de thumbnail YouTube 1280×720 (rosto+texto, conceitual, antes-depois) via gerar-imagem.",
        "quando_usar": "Acabou de gravar um vídeo longo e precisa de thumb pra subir.",
        "trigger": "'thumb yt', 'thumbnail', 'capa do video', 'miniatura youtube'",
        "exemplo": "thumb yt: [título do vídeo]",
    },
    {
        "slug": "repurpose-conteudo",
        "icone": "♻️",
        "tipo": "Especialista (orquestra outras)",
        "o_que_faz": "Pega 1 vídeo longo (live/podcast/masterclass) e devolve pacote multi-plataforma: 1 corte YouTube 8-15min + 3 Shorts/Reels + 1 carrossel + copys. Transcrição ElevenLabs (preferred) ou Whisper local (fallback).",
        "quando_usar": "Tem uma live de 1h e quer extrair conteúdo pra semana inteira em 1 comando.",
        "trigger": "'repurpose', 'transformar live', 'cortar masterclass', 'reaproveitar video'",
        "exemplo": "repurpose ~/Downloads/live.mp4",
    },
    {
        "slug": "gerar-copy-post",
        "icone": "✍️",
        "tipo": "Especialista",
        "o_que_faz": "Legenda + hashtags + CTA prontos pra colar no app. Adapta tom/formato por plataforma (Instagram, TikTok, YouTube, LinkedIn). Lê marca.json pra manter voz.",
        "quando_usar": "Já tem o conteúdo (foto/vídeo) e só precisa da legenda pra postar.",
        "trigger": "'copy reel', 'legenda ig', 'copy linkedin', 'descrição yt'",
        "exemplo": "gerar copy post instagram sobre [tema]",
    },
    {
        "slug": "gerar-imagem",
        "icone": "🎨",
        "tipo": "Helper (chamada por outras)",
        "o_que_faz": "Gateway de geração de imagem com fallback automático: gpt-image-2 (Codex CLI logado em ChatGPT) → Gemini Nano Banana → Higgsfield (opcional) → Imagen 4. Outras skills (carrossel/thumb) chamam esta — você raramente chama direto.",
        "quando_usar": "Quer 1 imagem solta pra qualquer uso (post avulso, banner, capa).",
        "trigger": "'gerar imagem', 'criar imagem', 'image2', 'nano banana'",
        "exemplo": "gerar imagem [descrição]",
    },
    {
        "slug": "gerar-video-mp4",
        "icone": "📹",
        "tipo": "Helper (chamada por criar-reel)",
        "o_que_faz": "Pipeline HTML animado → Chrome headless (Bun/puppeteer-core) → ffmpeg → MP4. Mesma engine dos anúncios ZX LAB. criar-reel chama internamente — você raramente chama direto.",
        "quando_usar": "Quer animação custom além do que criar-reel oferece (ex: hero animado pra LP).",
        "trigger": "'gerar video', 'render mp4', 'animação para reels'",
        "exemplo": "gerar video mp4 de [descrição]",
    },
]


def print_skills_explainer():
    """Imprime o que cada skill faz, quando usar, trigger e comando exemplo."""
    print("\n" + "=" * 70)
    print("📚 SUAS 8 SKILLS — o que cada uma faz")
    print("=" * 70)
    for s in SKILLS_DOCS:
        print(f"\n{s['icone']}  {s['slug']}   [{s['tipo']}]")
        print(f"   → {s['o_que_faz']}")
        print(f"   ✦ Quando usar:  {s['quando_usar']}")
        print(f"   ⚡ Triggers:     {s['trigger']}")
        print(f"   ▶  Exemplo:     {s['exemplo']}")
    print("\n" + "=" * 70)
    print("💡 As 2 últimas (gerar-imagem, gerar-video-mp4) são chamadas internamente")
    print("   pelas outras. No dia a dia você usa basicamente as 6 primeiras.")
    print("=" * 70 + "\n")


def dirs_equal(a: Path, b: Path) -> bool:
    if not (a.exists() and b.exists()):
        return False
    cmp = filecmp.dircmp(str(a), str(b))
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    for sub in cmp.common_dirs:
        if not dirs_equal(a / sub, b / sub):
            return False
    return True


def main():
    if not SKILLS_SRC.exists():
        print(f"❌ Pasta skills/ não encontrada em {SKILLS_SRC}")
        return 1

    SKILLS_DST.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    installed, updated, skipped, backupped = [], [], [], []

    for slug in EXPECTED:
        src = SKILLS_SRC / slug
        dst = SKILLS_DST / slug
        if not src.exists():
            print(f"❌ Skill faltando no repo: {slug}")
            return 1

        if not dst.exists():
            shutil.copytree(src, dst)
            installed.append(slug)
            continue

        if dirs_equal(src, dst):
            skipped.append(slug)
            continue

        backup = SKILLS_DST / f".s7-backup-{slug}-{ts}"
        shutil.copytree(dst, backup)
        shutil.rmtree(dst)
        shutil.copytree(src, dst)
        updated.append(slug)
        backupped.append(backup)

    print("\n📦 Resumo da instalação:")
    if installed: print(f"  ✅ Instaladas: {', '.join(installed)}")
    if updated:   print(f"  🔄 Atualizadas: {', '.join(updated)}")
    if skipped:   print(f"  ⏭  Já idênticas (puladas): {', '.join(skipped)}")
    if backupped:
        print("\n💾 Backups das versões anteriores:")
        for b in backupped:
            print(f"   • {b}")

    total = len(installed) + len(updated) + len(skipped)
    print(f"\n{total}/{len(EXPECTED)} skills no destino.")

    print_skills_explainer()

    print("Pronto para a Etapa 5 (Dashboard Local).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
