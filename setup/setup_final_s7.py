#!/usr/bin/env python3
"""
Setup 7 — Etapa 7: Finalização.
Marca phase_completed=7, abre dashboard.html no browser, imprime resumo + CTA.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from setup_base_s7 import ConfigBackupError, backup_config_copy, parse_phase, write_config_atomic  # noqa: E402

OPERACAO = Path.home() / ".operacao-ia"
CONFIG = OPERACAO / "config" / "config.json"
DASHBOARD = OPERACAO / "data" / "social-media" / "dashboard.html"


def mark_phase():
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text())
            if not isinstance(cfg, dict):
                raise ValueError("config.json não é um objeto JSON")
        except Exception:
            try:
                backup = backup_config_copy(CONFIG)
            except ConfigBackupError:
                sys.exit(1)  # mensagem ja impressa; config original intacto
            print(f"⚠️  config.json inválido — cópia guardada em {backup.name}")
            cfg = {}
    atual = parse_phase(cfg.get("phase_completed", 0))
    if atual < 7:  # nunca reduz um valor existente maior
        cfg["phase_completed"] = 7
    cfg["s7_installed_at"] = datetime.now().isoformat()
    write_config_atomic(cfg, CONFIG)
    print(f"✅ phase_completed={cfg['phase_completed']} (Setup 7 registrado) em {CONFIG}")


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
    print("\n🎁 Bônus opcional (fora das 8 etapas): publicação automática de 1 Reel/dia no Instagram.")
    print("   Quando quiser ativar, é só me pedir — eu configuro com você.")
    print("=" * 60)


def main():
    mark_phase()
    show_summary()
    open_dashboard()


if __name__ == "__main__":
    main()
