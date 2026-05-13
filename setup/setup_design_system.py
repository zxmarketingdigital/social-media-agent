#!/usr/bin/env python3
"""
Setup 7 — Etapa 2: Design System.
Aluno escolhe 1 dos 3 templates ou opta por custom (Claude gera DESIGN.md sob medida).
Grava ~/.operacao-ia/data/social-media/DESIGN.md.
"""
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates" / "design_systems"
DESIGN_DST = Path.home() / ".operacao-ia" / "data" / "social-media" / "DESIGN.md"

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
    if missing:
        print("❌ Templates de DESIGN.md faltando no repo:")
        for m in missing:
            print(f"   • {m}")
        print("   O repo parece corrompido. Reclone com: gh repo clone zxmarketingdigital/social-media-agent")
        sys.exit(1)


def main():
    validate_templates()
    show_options()
    choice = pick_choice()
    if choice == "custom":
        emit_custom_marker()
    else:
        copy_template(choice)
    print("\nPronto para a Etapa 3 (setup de transcrição: ElevenLabs + Whisper fallback).")


if __name__ == "__main__":
    main()
