#!/usr/bin/env python3
"""
check_prerequisites.py — Confere o ambiente antes de comecar o Setup 7.

Roda o MESMO diagnostico da Etapa 0 (Python, gh, Claude Code, ffmpeg, Chrome,
Bun, Codex/ChatGPT, Higgsfield, setups anteriores), mas em modo somente-leitura:
nao cria pastas, nao escreve config, nao instala nada. E idempotente — pode
rodar quantas vezes quiser.

Quem instala de fato e a Etapa 0 (`setup/setup_base_s7.py`); este arquivo e o
atalho pra saber, antes de comecar, se falta alguma coisa na maquina.

As checagens vivem em setup_base_s7.py (fonte unica) — aqui so orquestramos,
pra os dois nunca divergirem.

Compativel com Python 3.9 na leitura do arquivo (o setup em si pede 3.10+).
"""
import sys
from pathlib import Path
from typing import List, Tuple

# Permite rodar tanto da raiz (`python3 setup/check_prerequisites.py`)
# quanto de dentro da pasta setup/.
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import setup_base_s7 as base
except ImportError as e:  # pragma: no cover - so acontece em repo incompleto
    print("Nao consegui carregar setup/setup_base_s7.py: {}".format(e))
    print("Confirme que voce clonou o repositorio inteiro e tente de novo.")
    sys.exit(1)


# (rotulo, funcao, bloqueia?) — os 3 primeiros sao os mesmos bloqueantes da Etapa 0.
CHECAGENS = [
    ("Python 3.10+", base.check_python, True),
    ("gh CLI", base.check_gh, True),
    ("Claude Code CLI", base.check_claude_cli, True),
    ("ffmpeg", base.check_ffmpeg, False),
    ("Chrome/Chromium", base.check_chrome, False),
    ("Bun", base.check_bun, False),
    ("Codex CLI / ChatGPT", base.check_codex_or_chatgpt_cli, False),
    ("Higgsfield MCP", base.check_higgsfield_mcp, False),
    ("Setups anteriores", base.check_prior_setup, False),
]


def rodar() -> List[Tuple[str, bool]]:
    faltando = []
    for rotulo, funcao, bloqueia in CHECAGENS:
        try:
            ok = bool(funcao())
        except Exception as e:
            print("Nao foi possivel checar {}: {}".format(rotulo, e))
            ok = not bloqueia
        if bloqueia and not ok:
            faltando.append((rotulo, bloqueia))
    return faltando


def main() -> int:
    print("\nConferindo o que o Setup 7 (Social Media Agent) precisa...\n")

    faltando = rodar()

    print("")
    if faltando:
        print("Falta resolver antes de comecar:")
        for rotulo, _ in faltando:
            print("  - {}".format(rotulo))
        print("\nResolva os itens acima e rode este check de novo.")
        return 1

    print("Ambiente pronto. Pode abrir o Claude Code aqui e digitar: INICIAR SETUP SEMANA 7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
