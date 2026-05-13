#!/usr/bin/env python3
"""
Setup 7 — Etapa 7: Finalização.
Marca phase_completed=7, abre dashboard.html no browser, imprime resumo + CTA.
"""
import json
import subprocess
import sys
from pathlib import Path

OPERACAO = Path.home() / ".operacao-ia"
CONFIG = OPERACAO / "config" / "config.json"
DASHBOARD = OPERACAO / "data" / "social-media" / "dashboard.html"


def mark_phase():
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text())
        except Exception:
            cfg = {}
    cfg["phase_completed"] = max(cfg.get("phase_completed", 0), 7)
    cfg["s7_installed_at"] = __import__("datetime").datetime.now().isoformat()
    CONFIG.write_text(json.dumps(cfg, indent=2))
    print(f"✅ phase_completed=7 marcado em {CONFIG}")


def open_dashboard():
    if not DASHBOARD.exists():
        print(f"⚠️  Dashboard não encontrado em {DASHBOARD} — rode a Etapa 5 antes")
        return
    if sys.platform == "darwin":
        subprocess.run(["open", str(DASHBOARD)], check=False)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", str(DASHBOARD)], check=False)
    print(f"🌐 Dashboard aberto: {DASHBOARD}")


def show_summary():
    print("\n" + "=" * 60)
    print("✅ SETUP 7 CONCLUÍDO — Social Media Agent instalado")
    print("=" * 60)
    print("\n📌 Comandos prontos para uso:\n")
    print("   • criar reel sobre [tópico]")
    print("   • gerar carrossel [N] slides sobre [tema] para [plataforma]")
    print("   • thumb yt: [título]")
    print("   • gerar copy post [plataforma] sobre [tema]")
    print("   • repurpose [caminho do vídeo longo]")
    print("   • agente social  (abre menu com todas as opções)")
    print("\n📂 Outputs gerados ficam em:")
    print(f"   {OPERACAO}/data/social-media/output/{{reels,carrosseis,thumbs,stories,repurpose}}/")
    print("\n🎨 Para mudar o design system depois:")
    print(f"   edite {OPERACAO}/data/social-media/DESIGN.md")
    print("\n🚀 Próximos Setups do ZX Control:")
    print("   • Aula MasterClass do Setup 7: https://zx-control.zxlab.com.br")
    print("   • Comunidade: ZX LAB")
    print("=" * 60)


def main():
    mark_phase()
    show_summary()
    open_dashboard()


if __name__ == "__main__":
    main()
