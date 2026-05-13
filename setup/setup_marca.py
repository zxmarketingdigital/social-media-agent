#!/usr/bin/env python3
"""
Setup 7 — Etapa 1: Identidade da Marca.
Coleta nome, nicho, persona, tom e público. Grava marca.json.
"""
import json
import sys
from pathlib import Path

OPERACAO = Path.home() / ".operacao-ia"
MARCA_PATH = OPERACAO / "config" / "marca.json"

TONS = [
    ("profissional", "formal, técnico, autoridade"),
    ("acessivel",    "didático, próximo, conversacional"),
    ("provocador",   "ousado, contracorrente, opinativo"),
    ("inspirador",   "motivacional, otimista, aspiracional"),
    ("divertido",    "humorado, leve, irreverente"),
]


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    v = input(f"{prompt}{suffix}: ").strip()
    return v or default


def pick_tom() -> str:
    print("\nTom de voz da marca — escolha um:")
    for i, (slug, desc) in enumerate(TONS, 1):
        print(f"  {i}) {slug} — {desc}")
    while True:
        raw = input("Número (1-5): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 5:
            return TONS[int(raw) - 1][0]
        print("  Inválido. Digite 1, 2, 3, 4 ou 5.")


def main():
    print("\n📝 Identidade da Marca\n")

    existing = {}
    if MARCA_PATH.exists():
        try:
            existing = json.loads(MARCA_PATH.read_text())
            print(f"⚠️  marca.json já existe — confirme ou edite cada campo (Enter mantém atual)\n")
        except Exception as e:
            print(f"❌ marca.json existe mas está corrompido: {e}")
            backup = MARCA_PATH.with_suffix(".json.bak")
            MARCA_PATH.rename(backup)
            print(f"   Backup salvo em {backup}. Vou recoletar os campos do zero.\n")
            existing = {}

    nome = ask("Nome da marca (ex: Rafael Castro, ZX LAB)", existing.get("nome", ""))
    if not nome:
        print("❌ Nome é obrigatório.")
        sys.exit(1)

    nicho = ask("Nicho em 3-5 palavras (ex: IA aplicada a marketing)", existing.get("nicho", ""))
    if not nicho:
        print("❌ Nicho é obrigatório.")
        sys.exit(1)

    persona = ask("Descreva sua persona em 3 frases (quem você é, o que ensina, pra quem)", existing.get("persona", ""))
    publico = ask("Público-alvo principal (ex: empreendedores digitais 25-45 que querem escalar)", existing.get("publico", ""))

    tom_atual = existing.get("tom", "")
    if tom_atual:
        change = input(f"\nTom atual: {tom_atual}. Manter? (s/n) [s]: ").strip().lower()
        tom = tom_atual if change in ("", "s", "sim") else pick_tom()
    else:
        tom = pick_tom()

    instagram = ask("@ Instagram (sem o @, vazio se não tiver)", existing.get("instagram", ""))
    youtube = ask("Canal YouTube (URL ou @handle, vazio se não tiver)", existing.get("youtube", ""))
    tiktok = ask("@ TikTok (sem o @, vazio se não tiver)", existing.get("tiktok", ""))
    linkedin = ask("LinkedIn (URL do perfil, vazio se não tiver)", existing.get("linkedin", ""))

    marca = {
        "nome": nome,
        "nicho": nicho,
        "persona": persona,
        "publico": publico,
        "tom": tom,
        "handles": {
            "instagram": instagram,
            "youtube": youtube,
            "tiktok": tiktok,
            "linkedin": linkedin,
        },
    }

    MARCA_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARCA_PATH.write_text(json.dumps(marca, indent=2, ensure_ascii=False))

    print(f"\n✅ Identidade salva em {MARCA_PATH}")
    print(f"   Nome: {nome}")
    print(f"   Nicho: {nicho}")
    print(f"   Tom: {tom}")
    print("\nPronto para a Etapa 2 (Design System).")


if __name__ == "__main__":
    main()
