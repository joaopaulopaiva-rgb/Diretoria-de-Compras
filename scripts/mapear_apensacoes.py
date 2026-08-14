#!/usr/bin/env python3
"""
Varredura em massa de "Termo de Juntada por Apensação" (CLAUDE.md seção
4.6/12) para descobrir, sem precisar abrir processo por processo, em qual
processo de execução (Pregão/Dispensa/Inexigibilidade/Adesão SRP/...) cada
processo de Planejamento foi apensado.

Cada Termo de Juntada tem um texto-padrão confirmado empiricamente (ago/2026,
processos reais):

    "... faço apensar ao presente processo nº EXECUÇÃO o(s) processo(s)
    nº(s) APENSADO1[, APENSADO2 ...]. ..."

Ou seja, um documento só já revela o vínculo apensado→execução sem precisar
adivinhar nada. A busca (Tipo de Documento = 983, "Termo de Juntada por
Apensação") tem o mesmo teto de truncamento de 15 resultados por página que
a busca por Tipo de Processo — a varredura usa bisecção adaptativa de janela
de data pra nunca perder registro (mesma técnica do descoberta_semanal.py).

Uso:
    python3 scripts/mapear_apensacoes.py [--inicio 2024-01-01] [--fim hoje]

Saída: data/apensacoes_cache.json, atualizado incrementalmente (retomável —
semanas já varridas não são refeitas numa próxima execução).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, TIPO_DOCUMENTO, texto_visivel  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
CACHE_PATH = REPO_ROOT / "data" / "apensacoes_cache.json"

_NUM = r"\d{5}\.\d{6}/\d{4}-\d{2}"
_NUM_LIST = _NUM + r"(?:\s*(?:,|e)\s*" + _NUM + r")*"
_RE_EXECUCAO = re.compile(r"apensar ao presente processo n[ºo]\s*(" + _NUM + r")", re.IGNORECASE)
_RE_APENSADOS = re.compile(r"processo\(s\)\s*n[ºo]\(s\)\s*(" + _NUM_LIST + r")\.", re.IGNORECASE)
_RE_DATA_EMISSAO = re.compile(r"Natal-RN,\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})")
_MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
}


def _data_por_extenso_para_br(texto_data: str) -> str | None:
    m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", texto_data, re.IGNORECASE)
    if not m:
        return None
    dia, mes_nome, ano = m.groups()
    mes = _MESES.get(mes_nome.lower())
    if not mes:
        return None
    return f"{int(dia):02d}/{mes}/{ano}"


def carregar_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {"semanas_varridas": [], "apensacoes": {}, "docs_sem_padrao": []}


def salvar_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def buscar_com_janela_adaptativa(tipo_value: int, inicio: date, fim: date):
    """Cada chamada usa um SipacClient novo (sessão/cookie do zero) — achado
    empírico importante: reaproveitar a mesma sessão para buscas sucessivas
    de Tipo de Documento faz o SIPAC devolver resultado "preso" de uma busca
    anterior (mesmos ids, ignorando os novos parâmetros de data), mesmo que
    o HTTP responda 200 normalmente. buscar_processos_por_tipo não tem esse
    problema com sessão reaproveitada — é específico da busca de documento
    (formulário mais rico em AJAX/JSF, aparenta cachear estado de página no
    servidor). Confirmado repetindo a mesma janela e trocando de janela na
    mesma sessão: resultado não mudava até trocar de sessão."""
    resultados = SipacClient().buscar_documentos_por_tipo(tipo_value, inicio, fim)
    if inicio >= fim:
        return resultados
    meio = inicio + (fim - inicio) // 2
    if meio == inicio:
        return resultados
    if len(resultados) >= 15:
        parte1 = buscar_com_janela_adaptativa(tipo_value, inicio, meio)
        parte2 = buscar_com_janela_adaptativa(tipo_value, meio + timedelta(days=1), fim)
        return parte1 + parte2
    return resultados


def processar_documento(client: SipacClient, id_doc: int, cache: dict) -> None:
    html_doc = client.obter_documento_texto(id_doc)
    if html_doc is None:
        cache["docs_sem_padrao"].append({"id_doc": id_doc, "motivo": "sem visualização HTML (provável PDF puro)"})
        return
    texto = texto_visivel(html_doc)

    m_exec = _RE_EXECUCAO.search(texto)
    m_apen = _RE_APENSADOS.search(texto)
    if not m_exec or not m_apen:
        cache["docs_sem_padrao"].append({"id_doc": id_doc, "motivo": "texto não bateu com o padrão esperado", "trecho": texto[:400]})
        return

    execucao_numero = m_exec.group(1)
    apensados = re.findall(_NUM, m_apen.group(1))

    m_data = _RE_DATA_EMISSAO.search(texto)
    data_br = _data_por_extenso_para_br(m_data.group(1)) if m_data else None

    for numero_apensado in apensados:
        cache["apensacoes"][numero_apensado] = {
            "execucao_numero": execucao_numero,
            "data_apensacao": data_br,
            "id_doc_termo": id_doc,
        }


def varrer_semana(client: SipacClient, inicio_semana: date, fim_semana: date, cache: dict) -> int:
    resultados = buscar_com_janela_adaptativa(
        TIPO_DOCUMENTO["termo_juntada_apensacao"], inicio_semana, fim_semana
    )
    processados = 0
    for r in resultados:
        if r.id_doc is None:
            continue
        processar_documento(client, r.id_doc, cache)
        processados += 1
    return processados


def mapear(inicio: date, fim: date) -> dict:
    client = SipacClient()
    cache = carregar_cache()
    semanas_varridas = set(cache["semanas_varridas"])

    total_semanas = 0
    total_semanas_novas = 0
    total_docs_processados = 0

    cursor = inicio
    while cursor <= fim:
        fim_semana = min(cursor + timedelta(days=6), fim)
        chave_semana = f"{cursor.isoformat()}_{fim_semana.isoformat()}"
        total_semanas += 1
        if chave_semana not in semanas_varridas:
            total_docs_processados += varrer_semana(client, cursor, fim_semana, cache)
            semanas_varridas.add(chave_semana)
            cache["semanas_varridas"] = sorted(semanas_varridas)
            salvar_cache(cache)  # checkpoint a cada semana — retomável se interrompido
            total_semanas_novas += 1
        cursor = fim_semana + timedelta(days=1)

    return {
        "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
        "semanas_no_periodo": total_semanas,
        "semanas_novas_varridas_agora": total_semanas_novas,
        "documentos_processados_agora": total_docs_processados,
        "total_apensacoes_no_cache": len(cache["apensacoes"]),
        "total_docs_sem_padrao_no_cache": len(cache["docs_sem_padrao"]),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inicio", default="2024-01-01")
    parser.add_argument("--fim", default=None)
    args = parser.parse_args()

    inicio = date.fromisoformat(args.inicio)
    fim = date.fromisoformat(args.fim) if args.fim else date.today()

    resumo = mapear(inicio, fim)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
