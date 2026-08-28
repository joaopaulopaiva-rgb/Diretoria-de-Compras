#!/usr/bin/env python3
"""
Extrai o bloco de código ```json ... ``` do corpo de uma issue do GitHub
("Atualização do portão de entrada", gerada pelo clique em "Entrar no
painel" em docs/index.html — ver scripts/aplicar_decisoes.py e
.github/workflows/portao_atualizar.yml).

Se não houver bloco JSON (caso comum: clique sem decisão nenhuma pendente,
só pedindo a atualização geral), imprime uma lista vazia "[]" — o workflow
decide se roda aplicar_decisoes.py com base nisso.

Uso:
    python3 scripts/extrair_json_issue.py <arquivo_com_corpo_da_issue>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_BLOCO_JSON_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


def extrair(corpo: str) -> list:
    m = _BLOCO_JSON_RE.search(corpo)
    if not m:
        return []
    try:
        dados = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []
    return dados if isinstance(dados, list) else []


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python3 scripts/extrair_json_issue.py <arquivo>", file=sys.stderr)
        sys.exit(1)
    corpo = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(json.dumps(extrair(corpo), ensure_ascii=False))
