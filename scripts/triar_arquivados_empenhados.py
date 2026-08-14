#!/usr/bin/env python3
"""
Varre a fila do portão (data/portao_pendentes.json) procurando quatro sinais
no texto do ÚLTIMO documento do processo (mais o tipo de documento, pro
empenho) — validados contra 18 processos reais lidos manualmente. Só o
arquivamento remove da fila (confirmado explicitamente pela pessoa dona do
projeto); os outros três SINALIZAM (card de cor diferente) em vez de
remover, pra decisão manual — CLAUDE.md seção 14, não presumir.

  - Arquivamento explícito ("arquive-se", "arquivamento"...): decisão
    administrativa de encerrar o processo. Remove da fila (equivalente a
    "ignorar") — confiança alta, único caso com remoção automática.

  - Redirecionamento/segunda adesão resolvida ("deve ser apensado ao de
    número X", "a demanda será inserida no processo nº X", "o processo
    para acompanhamento é o X"...): a demanda foi (aparentemente)
    consolidada em OUTRO processo. Marca "alertaRedirecionado": true +
    "processoDestino" (número extraído, quando dá) — card azul.

  - Desistência explícita do requisitante ("desistência", "não tenho mais
    interesse"...): marca "alertaDesistencia": true — card diferenciado.

  - Empenho: "EMPENHO" no TIPO de algum documento (ex. "NOTA DE EMPENHO") —
    confiável só pelo tipo. Sinal de que HOUVE uma contratação de verdade
    que a varredura de apensação não conseguiu rastrear até o processo de
    execução — lacuna no levantamento, não processo morto. Marca
    "alertaEmpenhoSemExecucao": true — card âmbar.

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
_PADRAO_REDIRECT = re.compile(
    r"encaminhado anteriormente|deve ser apensado ao de n[úu]mero|ser[áa] inserida no processo|"
    r"seguiu para atendimento no processo|consultar o processo|para acompanhamento [ée] o",
    re.IGNORECASE,
)
_PADRAO_DESISTENCIA = re.compile(r"desist[êe]ncia|desistiu|desistimos|n[ãa]o tenho mais interesse", re.IGNORECASE)
_NUM_PROCESSO = re.compile(r"\d{5}\.\d{6}/\d{4}-\d{2}")


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


def _extrair_processo_destino(texto: str) -> str | None:
    m = _NUM_PROCESSO.search(texto)
    return m.group(0) if m else None


def triar(limite: int | None) -> dict:
    pendentes = carregar()
    client = SipacClient()

    processados = 0
    removidos_arquivamento = []
    sinalizados_redirect = []
    sinalizados_desistencia = []
    sinalizados_empenho = []
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
            tem_arquivamento = tem_redirect = tem_desistencia = False
            processo_destino = None
            if docs:
                texto_ultimo = texto_do_ultimo_documento(client, docs[-1])
                if texto_ultimo:
                    tem_arquivamento = bool(_PADRAO_ARQUIVAMENTO.search(texto_ultimo))
                    if not tem_arquivamento:
                        tem_redirect = bool(_PADRAO_REDIRECT.search(texto_ultimo))
                        if tem_redirect:
                            processo_destino = _extrair_processo_destino(texto_ultimo)
                        else:
                            tem_desistencia = bool(_PADRAO_DESISTENCIA.search(texto_ultimo))
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
            removidos_arquivamento.append(p["numero"])
            pendentes.pop(i)
            salvar(pendentes)
            continue

        p["triado"] = True
        if tem_redirect:
            p["alertaRedirecionado"] = True
            if processo_destino:
                p["processoDestino"] = processo_destino
            sinalizados_redirect.append({"numero": p["numero"], "processo_destino": processo_destino})
        elif tem_desistencia:
            p["alertaDesistencia"] = True
            sinalizados_desistencia.append(p["numero"])
        if tem_empenho:
            p["alertaEmpenhoSemExecucao"] = True
            sinalizados_empenho.append(p["numero"])
        salvar(pendentes)
        i += 1

    return {
        "processados_nesta_execucao": processados,
        "removidos_por_arquivamento": len(removidos_arquivamento),
        "sinalizados_redirecionamento": len(sinalizados_redirect),
        "numeros_sinalizados_redirecionamento": sinalizados_redirect,
        "sinalizados_desistencia": len(sinalizados_desistencia),
        "numeros_sinalizados_desistencia": sinalizados_desistencia,
        "sinalizados_com_empenho": len(sinalizados_empenho),
        "numeros_sinalizados_empenho": sinalizados_empenho,
        "falhas": falhas,
        "total_restante_no_portao": len(pendentes),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    args = parser.parse_args()

    resumo = triar(args.limite)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
