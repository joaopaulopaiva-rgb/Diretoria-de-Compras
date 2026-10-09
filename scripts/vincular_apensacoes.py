#!/usr/bin/env python3
"""
Aplica em data/processos.json os vínculos já descobertos por
scripts/mapear_apensacoes.py (data/apensacoes_cache.json).

Pedido explícito da pessoa dona do projeto (25/09/2026, reforçado
09/10/2026): assim que um planejamento na DPGC for apensado a um processo de
execução (Pregão/Dispensa/Inexigibilidade), os dois devem "andar juntos" no
painel — sem isso, o card continua mostrando "Planejamento (DPGC)" mesmo que
o processo já tenha passado por DFI/Jurídico/DFE de verdade.

mapear_apensacoes.py só descobre o NÚMERO do processo de execução (lido do
texto do Termo de Juntada). Esse script resolve o id interno do SIPAC
(a busca por número não funciona — CLAUDE.md seção 12 — mas dá pra achar
paginando a busca por Tipo de Processo, scripts/sipac_client.py
buscar_por_numero_paginado) e só then grava o vínculo.

Dois casos de baixa confiança NÃO são resolvidos automaticamente (CLAUDE.md
seção 10 — sinalizar, não presumir):
  - o número de destino não é encontrado no Tipo de Processo esperado pro
    caminho (ex. um "dispensa" cujo destino não aparece em Dispensa de
    Licitação nem em Inexigibilidade);
  - o número de destino aparece como Tipo=Planejamento (314) — sinal de que
    não é uma vinculação de execução de verdade, e sim um planejamento
    absorvido/remanejado por outro planejamento (caso real confirmado:
    23077.148564/2024-10 -> 23077.141816/2026-41).

Uso:
    python3 scripts/vincular_apensacoes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, TIPO_PROCESSO  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
PROCESSOS_PATH = REPO_ROOT / "data" / "processos.json"
CACHE_PATH = REPO_ROOT / "data" / "apensacoes_cache.json"

# Cada caminho usa nomes de campo próprios (CLAUDE.md seção 4) e um Tipo de
# Processo esperado pro destino (ver sipac_client.TIPO_PROCESSO).
CONFIG_CAMINHO = {
    "pregao": {"campo_numero": "pregao", "campo_id": "pregao_id", "tipo_execucao": TIPO_PROCESSO["pregao"]},
    "dispensa": {"campo_numero": "execucao_numero", "campo_id": "execucao_id", "tipo_execucao": TIPO_PROCESSO["dispensa"]},
    "inexigibilidade": {"campo_numero": "execucao_numero", "campo_id": "execucao_id", "tipo_execucao": TIPO_PROCESSO["inexigibilidade"]},
}


def vincular() -> dict:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    data = json.loads(PROCESSOS_PATH.read_text(encoding="utf-8"))
    client = SipacClient()

    aplicados = []
    ambiguos = []
    nao_resolvidos = []

    for p in data:
        caminho = p.get("caminho")
        config = CONFIG_CAMINHO.get(caminho)
        if not config or p.get("fase") == "Homologado":
            continue
        if p.get(config["campo_numero"]):
            continue  # já vinculado

        info = cache["apensacoes"].get(p["processo"])
        if not info:
            continue  # ainda não apareceu na varredura de Termos de Juntada

        destino_numero = info["execucao_numero"]

        resultado = client.buscar_por_numero_paginado(config["tipo_execucao"], destino_numero, max_paginas=25)
        if resultado:
            p[config["campo_numero"]] = destino_numero
            p[config["campo_id"]] = resultado.processo_id
            if p.get("avisoApensadoSemVinculo"):
                del p["avisoApensadoSemVinculo"]
            aplicados.append({"processo": p["processo"], "caminho": caminho, "destino": destino_numero, "destino_id": resultado.processo_id})
            continue

        resultado_planejamento = client.buscar_por_numero_paginado(TIPO_PROCESSO["planejamento"], destino_numero, max_paginas=25)
        if resultado_planejamento:
            ambiguos.append({
                "processo": p["processo"], "caminho": caminho, "destino": destino_numero,
                "motivo": "destino ainda é Tipo=Planejamento no SIPAC, não um processo de execução — provável planejamento absorvido por outro, não vinculação normal. NÃO aplicado.",
            })
            continue

        nao_resolvidos.append({
            "processo": p["processo"], "caminho": caminho, "destino": destino_numero,
            "motivo": f"destino não encontrado no Tipo de Processo esperado ({config['tipo_execucao']}) nem como Planejamento (314) — conferir manualmente.",
        })

    PROCESSOS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "aplicados": aplicados,
        "ambiguos": ambiguos,
        "nao_resolvidos": nao_resolvidos,
    }


if __name__ == "__main__":
    resumo = vincular()
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
