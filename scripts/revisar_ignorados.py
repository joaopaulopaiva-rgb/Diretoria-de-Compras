#!/usr/bin/env python3
"""
Revê data/ignorados.json (histórico de processos marcados "Ignorar" no
portão) e devolve à fila (data/portao_pendentes.json) qualquer um cuja
última atividade avançou desde que foi ignorado — sinal de que voltou a se
movimentar.

Rodado periodicamente (rotina bimestral, ver CLAUDE.md) pra não perder de
vista processos que "esfriaram" mas depois voltaram ao fluxo normal.

Uso:
    python3 scripts/revisar_ignorados.py

Salva incrementalmente — retomável se interrompido.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_documentos  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
IGNORADOS_PATH = REPO_ROOT / "data" / "ignorados.json"
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"

LINK_BASE = "https://sipac.ufrn.br/public/jsp/processos/processo_detalhado.jsf?id="


def carregar(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def salvar(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def revisar() -> dict:
    ignorados = carregar(IGNORADOS_PATH, [])
    pendentes = carregar(PENDENTES_PATH, [])
    pendentes_numeros = {p["numero"] for p in pendentes}
    client = SipacClient()

    voltaram = []
    ainda_parados = 0
    falhas = []

    restantes = []
    for ig in ignorados:
        if ig["numero"] in pendentes_numeros:
            # já está de volta na fila por algum outro motivo — mantém fora do histórico de ignorados
            continue
        try:
            html = client.obter_processo(ig["processo_id"])
            docs = extrair_documentos(html)
        except Exception as exc:  # noqa: BLE001
            falhas.append({"numero": ig["numero"], "erro": str(exc)})
            restantes.append(ig)
            continue

        ultima_atual = docs[-1].data if docs else None
        if ultima_atual and ultima_atual != ig.get("ultimaAtividadeNoMomento"):
            pendentes.append({
                "processo_id": ig["processo_id"],
                "numero": ig["numero"],
                "assunto": ig.get("assunto", ""),
                "primeiro_documento": None,
                "status": "pendente",
                "link": LINK_BASE + str(ig["processo_id"]),
                "descoberto_em": None,
                "nota_classificacao": (
                    f"voltou a se movimentar depois de ter sido ignorado em {ig.get('ignoradoEm')} "
                    f"(última atividade era {ig.get('ultimaAtividadeNoMomento')}, agora é {ultima_atual})"
                ),
            })
            voltaram.append(ig["numero"])
        else:
            ainda_parados += 1
            restantes.append(ig)

    salvar(IGNORADOS_PATH, restantes)
    salvar(PENDENTES_PATH, pendentes)

    return {
        "revisados": len(ignorados),
        "voltaram_ao_portao": len(voltaram),
        "numeros_que_voltaram": voltaram,
        "ainda_parados": ainda_parados,
        "falhas": falhas,
    }


if __name__ == "__main__":
    resumo = revisar()
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
