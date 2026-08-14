#!/usr/bin/env python3
"""
Revê os processos marcados como "Ignorar" no portão (data/ignorados.json)
pra checar se algum voltou a se movimentar desde que foi ignorado — se sim,
devolve pra fila do portão (data/portao_pendentes.json) com status
"pendente" de novo, pra reconsideração.

Critério: compara a data do documento mais recente HOJE com a que estava
registrada em "ultimaAtividadeNoIgnorar" (a última atividade no momento em
que a pessoa marcou "Ignorar"). Se mudou, o processo "criou vida" de novo.

Uso:
    python3 scripts/revisar_ignorados.py [--limite N]

Salva incrementalmente — retomável se interrompido.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_data_cadastro, extrair_documentos  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
IGNORADOS_PATH = REPO_ROOT / "data" / "ignorados.json"
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"


def carregar(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def salvar(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_data_br(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def revisar(limite: int | None) -> dict:
    ignorados = carregar(IGNORADOS_PATH, [])
    pendentes = carregar(PENDENTES_PATH, [])
    numeros_ja_pendentes = {p["numero"] for p in pendentes}
    client = SipacClient()

    processados = 0
    voltaram = []
    falhas = []

    i = 0
    while i < len(ignorados):
        item = ignorados[i]
        if limite is not None and processados >= limite:
            break

        try:
            html = client.obter_processo(item["processo_id"])
            docs = extrair_documentos(html)
        except Exception as exc:  # noqa: BLE001
            falhas.append({"processo_id": item["processo_id"], "numero": item.get("numero"), "erro": str(exc)})
            i += 1
            processados += 1
            continue

        processados += 1
        ultima_atual = docs[-1].data if docs else None
        data_ignorar = _parse_data_br(item.get("ultimaAtividadeNoIgnorar"))
        data_atual = _parse_data_br(ultima_atual)

        moveu = bool(data_atual and (not data_ignorar or data_atual > data_ignorar))

        if moveu and item["numero"] not in numeros_ja_pendentes:
            pendentes.append(
                {
                    "processo_id": item["processo_id"],
                    "numero": item["numero"],
                    "assunto": item.get("assunto", ""),
                    "primeiro_documento": None,
                    "status": "pendente",
                    "link": item.get("link", ""),
                    "descoberto_em": date.today().isoformat(),
                    "dataAbertura": extrair_data_cadastro(html),
                    "ultimaAtividade": ultima_atual,
                    "nota_classificacao": f"voltou a se movimentar depois de ter sido ignorado em {item.get('ignoradoEm')}",
                }
            )
            voltaram.append(item["numero"])
            ignorados.pop(i)
            salvar(PENDENTES_PATH, pendentes)
            salvar(IGNORADOS_PATH, ignorados)
            continue

        i += 1

    return {
        "processados_nesta_execucao": processados,
        "voltaram_ao_portao": len(voltaram),
        "numeros_que_voltaram": voltaram,
        "falhas": falhas,
        "total_ainda_ignorados": len(ignorados),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    args = parser.parse_args()

    resumo = revisar(args.limite)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
