#!/usr/bin/env python3
"""
Enriquece data/portao_pendentes.json com duas informações por processo:
"dataAbertura" (Data de Cadastro mostrada no cabeçalho da página pública)
e "ultimaAtividade" (data do documento mais recente — mesmo critério de
"última movimentação" usado no resumo mecânico de atualizar_marcos.py,
já que a tabela de Movimentações costuma vir vazia na maioria dos
processos, CLAUDE.md seção 12).

Substitui o campo "descoberto_em" (data em que a descoberta automática
achou o processo) exibido no portão — pouco útil pra decidir o que fazer
com um processo parado.

Uso:
    python3 scripts/enriquecer_portao.py [--limite N]

Salva incrementalmente (a cada processo) — retomável se interrompido.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_data_cadastro, extrair_documentos  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"


def carregar() -> list[dict]:
    return json.loads(PENDENTES_PATH.read_text(encoding="utf-8"))


def salvar(pendentes: list[dict]) -> None:
    PENDENTES_PATH.write_text(json.dumps(pendentes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enriquecer(limite: int | None) -> dict:
    pendentes = carregar()
    client = SipacClient()

    processados = 0
    falhas = []

    for p in pendentes:
        if "dataAbertura" in p:
            continue
        if limite is not None and processados >= limite:
            break

        try:
            html = client.obter_processo(p["processo_id"])
        except Exception as exc:  # noqa: BLE001 — segue pros outros processos
            falhas.append({"processo_id": p["processo_id"], "numero": p.get("numero"), "erro": str(exc)})
            continue

        docs = extrair_documentos(html)
        p["dataAbertura"] = extrair_data_cadastro(html)
        p["ultimaAtividade"] = docs[-1].data if docs else None

        processados += 1
        salvar(pendentes)  # checkpoint a cada processo

    return {
        "processados_nesta_execucao": processados,
        "falhas": falhas,
        "total_com_dados_no_cache": sum(1 for p in pendentes if "dataAbertura" in p),
        "total_no_portao": len(pendentes),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    args = parser.parse_args()

    resumo = enriquecer(args.limite)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
