#!/usr/bin/env python3
"""
Varre a fila do portão (data/portao_pendentes.json) procurando dois sinais:

  - Arquivamento explícito: o texto do ÚLTIMO documento do processo contém
    "arquiv..." (arquive-se, arquivamento, arquivado...). Testado contra 12
    processos reais lidos manualmente — checar só o TIPO do documento não
    basta (a maioria dos arquivamentos vem dentro de um "DESPACHO" genérico,
    não de um tipo "DESPACHO DE ARQUIVAMENTO" próprio); ler o texto do
    último documento acerta 100% na amostra de validação. Remove da fila do
    portão automaticamente (equivalente a "ignorar") — confiança alta.

  - Empenho: "EMPENHO" no TIPO de algum documento (ex. "NOTA DE EMPENHO") —
    esse sim é confiável só pelo tipo, não precisa ler texto. Sinal de que
    HOUVE uma contratação de verdade que a varredura de apensação não
    conseguiu rastrear até o processo de execução — lacuna no levantamento,
    não processo morto. NÃO remove da fila; marca com
    "alertaEmpenhoSemExecucao": true pra aparecer destacado na tela e a
    pessoa decidir (CLAUDE.md seção 14 — não presumir, sinalizar).

Uso:
    python3 scripts/triar_arquivados_empenhados.py [--limite N]

Salva incrementalmente (a cada processo) — retomável se interrompido. Marca
cada processo já visitado com "triado": true pra não reprocessar.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_documentos, texto_visivel  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"

_PADRAO_ARQUIVAMENTO = re.compile(r"arquiv(e|amento|ado|ar)", re.IGNORECASE)


def carregar() -> list[dict]:
    return json.loads(PENDENTES_PATH.read_text(encoding="utf-8"))


def salvar(pendentes: list[dict]) -> None:
    PENDENTES_PATH.write_text(json.dumps(pendentes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def texto_do_ultimo_documento(client: SipacClient, ultimo) -> str | None:
    if ultimo.id_doc:
        html_doc = client.obter_documento_texto(ultimo.id_doc)
        if html_doc:
            return texto_visivel(html_doc)
    if ultimo.id_arquivo and ultimo.arquivo_key:
        return client.obter_documento_pdf_texto(ultimo.id_arquivo, ultimo.arquivo_key)
    return None


def triar(limite: int | None) -> dict:
    pendentes = carregar()
    client = SipacClient()

    processados = 0
    removidos = []
    sinalizados = []
    falhas = []

    i = 0
    while i < len(pendentes):
        p = pendentes[i]
        if p.get("triado"):
            i += 1
            continue
        if limite is not None and processados >= limite:
            break

        try:
            html = client.obter_processo(p["processo_id"])
            docs = extrair_documentos(html)
            tipos = [d.tipo.upper() for d in docs]
            tem_empenho = any("EMPENHO" in t for t in tipos)
            tem_arquivamento = False
            if docs:
                texto_ultimo = texto_do_ultimo_documento(client, docs[-1])
                if texto_ultimo and _PADRAO_ARQUIVAMENTO.search(texto_ultimo):
                    tem_arquivamento = True
        except Exception as exc:  # noqa: BLE001
            falhas.append({"processo_id": p["processo_id"], "numero": p.get("numero"), "erro": str(exc)})
            p["triado"] = True
            p["triagemFalhou"] = True
            salvar(pendentes)
            processados += 1
            i += 1
            continue

        processados += 1

        if tem_arquivamento:
            removidos.append(p["numero"])
            pendentes.pop(i)  # remove — não incrementa i, o próximo item ocupa essa posição
            salvar(pendentes)
            continue

        p["triado"] = True
        if tem_empenho:
            p["alertaEmpenhoSemExecucao"] = True
            sinalizados.append(p["numero"])
        salvar(pendentes)
        i += 1

    return {
        "processados_nesta_execucao": processados,
        "removidos_por_arquivamento": len(removidos),
        "numeros_removidos": removidos,
        "sinalizados_com_empenho": len(sinalizados),
        "numeros_sinalizados": sinalizados,
        "falhas": falhas,
        "total_restante_no_portao": len(pendentes),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    args = parser.parse_args()

    resumo = triar(args.limite)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
