#!/usr/bin/env python3
"""
Setup 7 — Etapa 2: Design System.
Aluno escolhe 1 dos 3 templates ou opta por custom (Claude gera DESIGN.md sob medida).
Grava ~/.operacao-ia/data/social-media/DESIGN.md.

Subpasso (executado pelo Claude após gravar o DESIGN.md):
Gerar `design-showcase.html` em ~/.operacao-ia/data/social-media/ adaptando
o template de referência em `templates/design-showcase-template.html` para
as cores/tipografia/marca do aluno. Abrir no browser e pedir aprovação.
"""
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates" / "design_systems"
SHOWCASE_TEMPLATE = REPO_ROOT / "templates" / "design-showcase-template.html"
SOCIAL_DIR = Path.home() / ".operacao-ia" / "data" / "social-media"
DESIGN_DST = SOCIAL_DIR / "DESIGN.md"
SHOWCASE_DST = SOCIAL_DIR / "design-showcase.html"
MARCA = Path.home() / ".operacao-ia" / "config" / "marca.json"

TEMPLATES_DESC = [
    ("dark-mono",       "minimalista escuro, mono-fonte — tech, finance, B2B"),
    ("light-editorial", "claro editorial com serif — lifestyle, wellness, educação"),
    ("vivid-pop",       "colorido vibrante — entretenimento, food, fitness"),
    ("custom",          "descreva cor/estilo/referências e Claude gera sob medida"),
]


def show_options():
    print("\n🎨 Escolha um design system:\n")
    for i, (slug, desc) in enumerate(TEMPLATES_DESC, 1):
        print(f"  {i}) {slug} — {desc}")


def pick_choice() -> str:
    while True:
        raw = input("\nNúmero (1-4): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 4:
            return TEMPLATES_DESC[int(raw) - 1][0]
        print("  Inválido. Digite 1, 2, 3 ou 4.")


def copy_template(slug: str):
    src = TEMPLATES / slug / "DESIGN.md"
    if not src.exists():
        print(f"❌ Template {slug} não encontrado em {src}")
        sys.exit(1)
    DESIGN_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, DESIGN_DST)
    print(f"\n✅ Design system '{slug}' instalado em {DESIGN_DST}")


def emit_custom_marker():
    """
    Quando o aluno escolhe 'custom', cria um arquivo placeholder e instrui o Claude
    a coletar cor/estilo/referências e escrever o DESIGN.md sob medida.
    """
    DESIGN_DST.parent.mkdir(parents=True, exist_ok=True)
    DESIGN_DST.write_text("# DESIGN.md — pendente de geração customizada\n\n"
                          "Este arquivo será reescrito pelo Claude após coletar as referências da marca.\n")
    print(f"\n📝 Modo custom selecionado. {DESIGN_DST}")
    print("\n>>> CLAUDE: agora colete do aluno:")
    print("    1) Cor primária (hex ou descrição)")
    print("    2) Cor de destaque (hex ou descrição)")
    print("    3) Estilo visual (minimalista, editorial, vibrante, retro, brutalista, etc.)")
    print("    4) 2-3 referências (nomes de marcas ou perfis que ele admira)")
    print("    5) Tipografia (serif, sans, mono, ou mista)")
    print(f"\nDepois, escreva o DESIGN.md completo em {DESIGN_DST}")
    print("seguindo o padrão dos templates em templates/design_systems/dark-mono/DESIGN.md")
    print("(seções: Cores, Tipografia, Espaçamento, Estilo visual, Componentes).")


def validate_templates():
    missing = []
    for slug, _ in TEMPLATES_DESC[:-1]:  # skip "custom"
        src = TEMPLATES / slug / "DESIGN.md"
        if not src.exists():
            missing.append(str(src))
    if not SHOWCASE_TEMPLATE.exists():
        missing.append(str(SHOWCASE_TEMPLATE))
    if missing:
        print("❌ Templates faltando no repo:")
        for m in missing:
            print(f"   • {m}")
        print("   O repo parece corrompido. Reclone com: gh repo clone zxmarketingdigital/social-media-agent")
        sys.exit(1)


def emit_showcase_instructions(choice: str):
    """
    Imprime instruções para o Claude gerar o design-showcase.html adaptado
    à marca do aluno, abrir no browser e pedir aprovação antes de avançar.
    O DESIGN.md já foi gravado por copy_template() ou emit_custom_marker().
    """
    print("\n" + "=" * 60)
    print("📐 SUBPASSO — Gerar Design Showcase (HTML pra aprovação)")
    print("=" * 60)
    print()
    print(">>> CLAUDE: agora gere o design-showcase.html da marca do aluno.")
    print()
    print("1. Leia os 3 inputs:")
    print(f"     • Template de referência:  {SHOWCASE_TEMPLATE}")
    print(f"     • DESIGN.md do aluno:      {DESIGN_DST}")
    print(f"     • marca.json:              {MARCA}  (nome, nicho, persona, tom, handles)")
    print()
    print("2. Adapte o template de referência mantendo a MESMA estrutura visual:")
    print("     - Header (logo + subtitle + desc)")
    print("     - Seção 01 Paleta (swatches em grid, com hex tokens)")
    print("     - Seção 02 Tipografia (hierarquia: display, headline, body, label, metric)")
    print("     - Seção 03 Mockups (4 slides carrossel + 2 reels + 1 thumb YouTube)")
    print("     - Seção 04 Componentes (badge, métrica, CTA, antes/depois)")
    print("     - Seção 05 Do's & Don'ts")
    print("     - Footer")
    print()
    print("3. Substitua nos slides/reels/thumb:")
    print("     • Logo / handle / @user      → marca.json (nome, handles.instagram)")
    print("     • Cores / fontes / tokens    → DESIGN.md do aluno")
    print("     • Hooks / headlines / copys  → ângulo do nicho do aluno (mantenha tom da marca)")
    print("     • Métricas exemplo           → exemplos plausíveis pro nicho dele")
    print()
    print(f"4. Salve em: {SHOWCASE_DST}")
    print()
    print(f"5. Abra no browser:  open {SHOWCASE_DST}")
    print()
    print("6. Pergunte ao aluno: 'Aprovado? (s/n/ajustar)'")
    print("     • s        → marca a etapa concluída e avança pra Etapa 3 (Transcrição).")
    print("     • n        → volte ao menu da Etapa 2 (refazer escolha do design system).")
    print("     • ajustar  → o aluno descreve o que quer mudar; você atualiza DESIGN.md +")
    print("                  regenera o showcase, e pergunta de novo.")
    print()
    print(f"   Loop até aprovação. O template de referência tem ~785 linhas — use como")
    print("   esqueleto exato de HTML/CSS, só ajustando tokens e copy.")
    print()


def main():
    validate_templates()
    show_options()
    choice = pick_choice()
    if choice == "custom":
        emit_custom_marker()
    else:
        copy_template(choice)
    emit_showcase_instructions(choice)
    print("\nApós aprovação do showcase pelo aluno, prossiga para a Etapa 3 (setup de transcrição: ElevenLabs + Whisper fallback).")


if __name__ == "__main__":
    main()
