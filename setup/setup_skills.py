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
    print(f"\n{total}/{len(EXPECTED)} skills no destino. Pronto para a Etapa 5.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
