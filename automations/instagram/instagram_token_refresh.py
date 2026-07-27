#!/usr/bin/env python3
"""
instagram_token_refresh.py — mantem o token do Instagram vivo.

O token de longa duracao do Instagram vale 60 dias. A Meta deixa renovar ele
quando tem MAIS de 24 horas e MENOS de 60 dias de idade. Rodando 1x por semana,
ele nunca expira. Se passar dos 60 dias, renovar nao resolve mais — ai voce
precisa gerar um token novo (o guia explica como).

O que este script faz:
  1. Le o token atual de ~/.operacao-ia/config/instagram.env
  2. Pede um token novo pra Meta
  3. Faz uma copia de seguranca do arquivo antes de trocar
  4. Grava o token novo no lugar do antigo, preservando o resto do arquivo

Uso:
  python3 instagram_token_refresh.py             renova
  python3 instagram_token_refresh.py --dry-run   testa sem gravar nada

Compatibilidade: Python 3.9+ (sem sintaxe 3.10+). So biblioteca padrao.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig_common as ig  # noqa: E402

LOG_NAME = "ig-token-refresh.log"
KEEP_BACKUPS = 12

# A Meta so aceita renovar um token com MAIS de 24h de idade. Sem esta guarda,
# quem configura o bonus no domingo a noite recebe um "falhei" na segunda de
# manha por um comportamento totalmente esperado.
MIN_TOKEN_AGE = timedelta(hours=24)


def log(msg: str, level: str = "INFO") -> None:
    ig.log(msg, level, log_name=LOG_NAME)


def prune_backups() -> None:
    """Mantem so as copias de seguranca mais recentes."""
    try:
        pattern = ig.ENV_PATH.name + ".bak.*"
        backups = sorted(ig.ENV_PATH.parent.glob(pattern))
        for old in backups[:-KEEP_BACKUPS]:
            try:
                old.unlink()
            except OSError:
                pass
    except Exception:
        pass


def token_age(env) -> Optional[timedelta]:
    """Idade do token atual, se o carimbo existir e for legivel."""
    raw = (env.get("IG_TOKEN_GENERATED_AT") or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.now() - datetime.strptime(raw[:19], fmt)
        except ValueError:
            continue
    return None


def write_env_update(new_token: str, generated_at: str) -> None:
    """Grava o token novo preservando a ordem das linhas do arquivo.

    Faz uma copia de seguranca com data/hora ANTES de qualquer escrita, e usa
    escrita atomica: se o processo morrer no meio, o arquivo nao fica truncado
    (o publicador pode estar lendo ele ao mesmo tempo).

    Se a linha do token nao for encontrada, NAO grava e levanta erro. Antes
    disso, um arquivo editado a mao (espaco antes da chave, linha comentada)
    fazia o token novo ser descartado em silencio — e o script ainda dizia
    "renovado com sucesso" toda semana ate o token morrer aos 60 dias.
    """
    text = ig.ENV_PATH.read_text()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = ig.ENV_PATH.parent / ("%s.bak.%s" % (ig.ENV_PATH.name, stamp))
    ig.atomic_write(backup, text)
    prune_backups()

    # \s* aceita o arquivo com indentacao, mas NAO aceita linha comentada.
    text, trocas = re.subn(r"(?m)^[ \t]*IG_ACCESS_TOKEN[ \t]*=.*$",
                           "IG_ACCESS_TOKEN=" + new_token, text, count=1)
    if trocas == 0:
        raise RuntimeError(
            "nao encontrei a linha IG_ACCESS_TOKEN= em %s. O token NOVO nao foi "
            "gravado (preferi falhar a fingir que deu certo). Se voce editou o "
            "arquivo a mao, deixe a linha exatamente como IG_ACCESS_TOKEN=... e "
            "sem # na frente — ou rode %s de novo."
            % (ig.ENV_PATH, ig.SETUP_HINT))

    text, trocas_carimbo = re.subn(r"(?m)^[ \t]*IG_TOKEN_GENERATED_AT[ \t]*=.*$",
                                   "IG_TOKEN_GENERATED_AT=" + generated_at,
                                   text, count=1)
    if trocas_carimbo == 0:
        text = text.rstrip() + "\nIG_TOKEN_GENERATED_AT=" + generated_at + "\n"

    ig.atomic_write(ig.ENV_PATH, text)

    # Confere o que ficou no disco: gravar e nao valer e o pior dos mundos.
    conferido = ig.load_ig_env().get("IG_ACCESS_TOKEN")
    if conferido != new_token:
        raise RuntimeError(
            "gravei %s mas o token lido de volta nao e o novo. A copia de "
            "seguranca esta em %s." % (ig.ENV_PATH, backup.name))


def refresh(dry_run: bool = False) -> int:
    env = ig.load_ig_env()
    ig.env_secrets(env)
    token = env.get("IG_ACCESS_TOKEN")
    if not token:
        print("⚠️  Nao encontrei IG_ACCESS_TOKEN em %s." % ig.ENV_PATH)
        print("   Rode %s para configurar." % ig.SETUP_HINT)
        log("IG_ACCESS_TOKEN ausente", "ERROR")
        return 2

    idade = token_age(env)
    if idade is not None and idade < MIN_TOKEN_AGE:
        horas = int(idade.total_seconds() // 3600)
        print("ℹ️  Token gerado ha %sh — a Meta so renova depois de 24h." % horas)
        print("   Nao e erro: renovo sozinho na proxima semana.")
        log("token com %sh de idade — pulando (Meta exige >24h)" % horas)
        return 0

    # ATENCAO — NAO "corrigir" isto para Authorization: Bearer.
    # Este endpoint especifico IGNORA o header Authorization e responde
    # 400 IGApiException code 100 "The parameter access_token is required".
    # Comprovado em producao: quando alguem trocou pra header, o refresh parou
    # de funcionar e o token expirou. O token vai na query string DE PROPOSITO.
    # Seguranca: str(HTTPError) nao inclui a URL, e redact() cobre
    # `access_token=` e o valor literal do token em todo log/saida.
    url = ig.IG_REFRESH_URL + "?" + urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token})
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=20) as r:
            payload = json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        # Sem ler o corpo, a mensagem viraria so "HTTP Error 400: Bad Request" —
        # e a tabela de erros do guia (indexada por 'code 190', 'access_token is
        # required') nunca casaria com nada do que o aluno ve.
        corpo = ""
        try:
            corpo = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        detalhe = ig.redact(corpo).strip() or ig.safe_error_repr(e)
        print("❌ A Meta recusou a renovacao do token (HTTP %s)."
              % getattr(e, "code", "?"))
        print("   Resposta da Meta: %s" % detalhe[:500])
        print("   Se aparecer 'code 190' ou token expirado, o caminho e gerar um")
        print("   token novo. Passo a passo: %s" % ig.DOC_HINT)
        log("refresh recusado (HTTP %s): %s" % (getattr(e, "code", "?"), detalhe[:500]),
            "ERROR")
        ig.notify_local("Nao consegui renovar o token do Instagram.")
        return 3
    except Exception as e:
        print("❌ Nao consegui falar com a Meta para renovar o token.")
        print("   Detalhe: %s" % ig.safe_error_repr(e))
        print("   Se o problema persistir, confira a sua conexao e o guia: %s"
              % ig.DOC_HINT)
        log("falha HTTP no refresh: %s" % ig.safe_error_repr(e), "ERROR")
        ig.notify_local("Nao consegui renovar o token do Instagram.")
        return 3

    new_token = payload.get("access_token")
    expires_in = payload.get("expires_in")
    if not new_token:
        # NUNCA logar o corpo cru — pode conter token dentro da mensagem de erro.
        log("resposta sem token novo (campos: %s)" % list(payload.keys()), "ERROR")
        print("❌ A Meta respondeu sem um token novo.")
        print("   Isso costuma significar que o token passou dos 60 dias e "
              "precisa ser gerado de novo. Passo a passo: %s" % ig.DOC_HINT)
        ig.notify_local("Token do Instagram precisa ser gerado de novo.")
        return 4

    ig.register_secret(new_token)
    days = (expires_in or 0) // 86400

    if dry_run:
        print("✅ Teste OK: a Meta aceitou renovar (validade nova: %s dias)." % days)
        print("   Nada foi gravado (--dry-run).")
        log("[dry-run] refresh aceito, validade %sd" % days)
        return 0

    generated_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        write_env_update(new_token, generated_at)
    except Exception as e:
        print("❌ Renovei o token mas nao consegui gravar em %s." % ig.ENV_PATH)
        print("   Detalhe: %s" % ig.safe_error_repr(e))
        log("falha ao gravar env: %s" % ig.safe_error_repr(e), "ERROR")
        ig.notify_local("Falha ao gravar o token novo do Instagram.")
        return 5

    log("token renovado — validade de %s dias" % days)
    print("✅ Token do Instagram renovado (validade: %s dias)." % days)
    return 0


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    try:
        return refresh(dry_run=dry_run)
    except ig.ConfigError as e:
        print("\n⚠️  %s\n" % ig.redact(e))
        return 2
    except KeyboardInterrupt:
        print("\nCancelado.")
        return 130
    except Exception as e:
        # Rede de seguranca: o aluno nunca deve ver um traceback do Python.
        print("\n❌ Nao consegui renovar o token do Instagram.")
        print("   Detalhe: %s" % ig.safe_error_repr(e))
        print("   Guia: %s\n" % ig.DOC_HINT)
        try:
            log("erro inesperado: %s" % ig.safe_error_repr(e), "ERROR")
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
