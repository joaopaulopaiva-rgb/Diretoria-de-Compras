#!/usr/bin/env python3
"""
Varre a fila do portão (data/portao_pendentes.json) usando o campo "Status"
oficial da própria página pública do processo (mais confiável que adivinhar
pelo texto do último documento, usado em triar_arquivados_empenhados.py):

  - Status "CANCELADO" ou "SOLICITADO CANCELAMENTO" → remove da fila.
  - Status começando com "ARQUIVADO" (o campo inclui carimbo de data/hora,
    ex. "ARQUIVADO (Em 15/04/2024 09:53)") → remove da fila.
  - Status "APENSADO" → NÃO remove; só registra em
    data/apensados_ainda_no_portao.json pra análise separada (achar pra
    onde cada um foi apensado), já que o processo pode ainda representar
    uma contratação real que precisa ser rastreada em outro lugar.

Uso:
    python3 scripts/limpar_cancelados_arquivados.py [--limite N]

Salva incrementalmente — retomável se interrompido. Marca cada processo já
visitado com "statusChecado": true.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"
APENSADOS_PATH = REPO_ROOT / "data" / "apensados_ainda_no_portao.json"

_PADRAO_STATUS = re.compile(r"<th><b>Status:</b></th>\s*<td>\s*([^<]+?)\s*</td>", re.IGNORECASE)


def carregar(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def salvar(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def limpar(limite: int | None) -> dict:
    pendentes = carregar(PENDENTES_PATH, [])
    apensados = carregar(APENSADOS_PATH, [])
    apensados_ja_vistos = {a["numero"] for a in apensados}
    client = SipacClient()

    processados = 0
    removidos_cancelado = []
    removidos_arquivado = []
    novos_apensados = []
    falhas = []

    i = 0
    while i < len(pendentes):
        p = pendentes[i]
        if p.get("statusChecado"):
            i += 1
            continue
        if limite is not None and processados >= limite:
            break

        try:
            html = client.obter_processo(p["processo_id"])
        except Exception as exc:  # noqa: BLE001
            falhas.append({"processo_id": p["processo_id"], "numero": p.get("numero"), "erro": str(exc)})
            p["statusChecado"] = True
            salvar(PENDENTES_PATH, pendentes)
            processados += 1
            i += 1
            continue

        m = _PADRAO_STATUS.search(html)
        status = m.group(1).strip() if m else None
        processados += 1

        if status and ("CANCELADO" in status.upper()):
            removidos_cancelado.append({"numero": p["numero"], "status": status})
            pendentes.pop(i)
            salvar(PENDENTES_PATH, pendentes)
            continue

        if status and status.upper().startswith("ARQUIVADO"):
            removidos_arquivado.append({"numero": p["numero"], "status": status})
            pendentes.pop(i)
            salvar(PENDENTES_PATH, pendentes)
            continue

        if status == "APENSADO" and p["numero"] not in apensados_ja_vistos:
            novos_apensados.append({"numero": p["numero"], "processo_id": p["processo_id"], "assunto": p.get("assunto", "")})
            apensados_ja_vistos.add(p["numero"])

        p["statusChecado"] = True
        salvar(PENDENTES_PATH, pendentes)
        i += 1

    if novos_apensados:
        apensados.extend(novos_apensados)
        salvar(APENSADOS_PATH, apensados)

    return {
        "processados_nesta_execucao": processados,
        "removidos_por_cancelamento": len(removidos_cancelado),
        "removidos_por_arquivamento_status": len(removidos_arquivado),
        "novos_apensados_registrados": len(novos_apensados),
        "total_apensados_para_analise": len(apensados),
        "falhas": falhas,
        "total_restante_no_portao": len(pendentes),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    args = parser.parse_args()

    resumo = limpar(args.limite)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
