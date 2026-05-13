#!/usr/bin/env python3
"""
Setup 7 — Etapa 6: Demo de Geração.
Este script NÃO chama Higgsfield diretamente — apenas valida estado e imprime
as instruções para o Claude invocar as skills `gerar-carrossel` e `criar-reel`
usando marca.json + DESIGN.md.
"""
import json
import subprocess
import sys
from pathlib import Path

DATA = Path.home() / ".operacao-ia" / "data" / "social-media"
CFG = Path.home() / ".operacao-ia" / "config"
MARCA = CFG / "marca.json"
DESIGN = DATA / "DESIGN.md"
DEMO_DIR = DATA / "output" / "demo"


def check_higgsfield_connected():
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True, text=True, timeout=15,
        )
        out = (result.stdout + result.stderr).lower()
        if "higgsfield" in out and "connected" in out:
            return True
        return False
    except Exception:
        return False


def main():
    # validar estado
    if not MARCA.exists():
        print("❌ marca.json não encontrado. Conclua a Etapa 1 antes.")
        sys.exit(1)
    if not DESIGN.exists():
        print("❌ DESIGN.md não encontrado. Conclua a Etapa 2 antes.")
        sys.exit(1)
    if not check_higgsfield_connected():
        print("❌ Higgsfield MCP não conectado.")
        print("   Conecte com: claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp")
        print("   Faça login pelo browser quando solicitado, e rode esta etapa novamente.")
        sys.exit(1)

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
    print(f"   Output: {DEMO_DIR}\n")

    print(">>> CLAUDE: agora invoque as 2 skills abaixo, NESTA ORDEM, salvando em output/demo/")
    print()
    print("    1) Skill: gerar-carrossel")
    print(f"       Prompt: '5 slides apresentando a marca {nome} para {publico} no nicho de {nicho}.")
    print(f"               Tom: {tom}. Estrutura: capa, problema, 3 pontos, CTA. Plataforma: Instagram.'")
    print(f"       Output dir: {DEMO_DIR}/carrossel-apresentacao/")
    print()
    print("    2) Skill: criar-reel")
    print(f"       Prompt: 'Reel 30 segundos com avatar AI apresentando {nome}.")
    print(f"               Hook: \"Você sabia que [insight do nicho {nicho}]?\".")
    print(f"               Corpo: 2 ideias-chave. CTA final: seguir o perfil. Tom: {tom}.")
    print("                Plataforma: Instagram, 9:16.'")
    print(f"       Output: {DEMO_DIR}/reel-apresentacao.mp4")
    print()
    print("    Após cada geração, atualize gallery.json adicionando o item criado.")
    print()
    print("    Se Higgsfield retornar erro ou rate limit:")
    print("    - Mostre a mensagem técnica ao aluno em linguagem clara")
    print("    - Sugira tentar novamente em 5-10 minutos")
    print("    - Não pule a etapa silenciosamente")
    print()
    print("Quando ambas as gerações concluírem, avance para a Etapa 7 (finalização).")


if __name__ == "__main__":
    main()
