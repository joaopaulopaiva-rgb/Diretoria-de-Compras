#!/usr/bin/env python3
"""
Varredura histórica de processos por Tipo de Processo (Planejamento +
os 4 caminhos de execução com tipo próprio: Pregão, Dispensa,
Inexigibilidade, Adesão SRP, Concorrência), de 01/01/2024 até hoje.

Objetivo: montar um índice completo {número → (id, assunto)} pra cada tipo,
sem precisar abrir processo por processo. Combinado com o mapeamento de
apensações já feito (scripts/mapear_apensacoes.py → data/apensacoes_cache.json),
isso permite classificar automaticamente o caminho de cada processo de
Planejamento: acha o número dele nas apensações → pega o número do processo
de execução vinculado → procura esse número neste índice → o tipo em que
achou é o caminho.

Mesma técnica de bisecção adaptativa de janela usada em
descoberta_semanal.py e mapear_apensacoes.py (teto de 15 resultados por
página do SIPAC). Diferente da busca por Tipo de Documento, a busca por
Tipo de Processo não teve o bug de sessão "presa" entre buscas sucessivas
(reconfirmado empiricamente) — reaproveita o client à vontade aqui.

Uso:
    python3 scripts/descobrir_historico_processos.py [--inicio 2024-01-01] [--fim hoje]

Saída: data/processos_index_cache.json, atualizado incrementalmente por tipo
(retomável — combinações tipo+semana já varridas não são refeitas).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, TIPO_PROCESSO  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
CACHE_PATH = REPO_ROOT / "data" / "processos_index_cache.json"

# Só os tipos com valor próprio de busca confirmado — Concorrência que nasce
# direto na Compras (rascunho, seção 4.4 do CLAUDE.md) e Contrata+Brasil não
# têm tipo de processo próprio identificado ainda, ficam fora desta varredura.
TIPOS_A_VARRER = ["planejamento", "pregao", "dispensa", "inexigibilidade", "adesao_srp", "concorrencia"]


def carregar_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {tipo: {"semanas_varridas": [], "processos": {}} for tipo in TIPOS_A_VARRER}


def salvar_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def buscar_com_janela_adaptativa(client: SipacClient, tipo_value: int, inicio: date, fim: date):
    resultados = client.buscar_processos_por_tipo(tipo_value, inicio, fim)
    if inicio >= fim:
        return resultados
    meio = inicio + (fim - inicio) // 2
    if meio == inicio:
        return resultados
    if len(resultados) >= 15:
        parte1 = buscar_com_janela_adaptativa(client, tipo_value, inicio, meio)
        parte2 = buscar_com_janela_adaptativa(client, tipo_value, meio + timedelta(days=1), fim)
        return parte1 + parte2
    return resultados


def varrer_tipo(client: SipacClient, tipo: str, inicio: date, fim: date, cache: dict) -> dict:
    tipo_value = TIPO_PROCESSO[tipo]
    bloco = cache[tipo]
    semanas_varridas = set(bloco["semanas_varridas"])

    total_semanas = 0
    semanas_novas = 0
    processos_novos = 0

    cursor = inicio
    while cursor <= fim:
        fim_semana = min(cursor + timedelta(days=6), fim)
        chave_semana = f"{cursor.isoformat()}_{fim_semana.isoformat()}"
        total_semanas += 1
        if chave_semana not in semanas_varridas:
            resultados = buscar_com_janela_adaptativa(client, tipo_value, cursor, fim_semana)
            for r in resultados:
                if r.processo_id is None:
                    continue
                if r.numero not in bloco["processos"]:
                    processos_novos += 1
                bloco["processos"][r.numero] = {"id": r.processo_id, "assunto": r.assunto}
            semanas_varridas.add(chave_semana)
            bloco["semanas_varridas"] = sorted(semanas_varridas)
            salvar_cache(cache)  # checkpoint a cada semana — retomável se interrompido
            semanas_novas += 1
        cursor = fim_semana + timedelta(days=1)

    return {
        "tipo": tipo,
        "semanas_no_periodo": total_semanas,
        "semanas_novas_varridas_agora": semanas_novas,
        "processos_novos_agora": processos_novos,
        "total_processos_no_cache": len(bloco["processos"]),
    }


def descobrir_tudo(inicio: date, fim: date) -> list[dict]:
    client = SipacClient()
    cache = carregar_cache()
    resumos = []
    for tipo in TIPOS_A_VARRER:
        resumos.append(varrer_tipo(client, tipo, inicio, fim, cache))
    return resumos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inicio", default="2024-01-01")
    parser.add_argument("--fim", default=None)
    args = parser.parse_args()

    inicio = date.fromisoformat(args.inicio)
    fim = date.fromisoformat(args.fim) if args.fim else date.today()

    resumo = descobrir_tudo(inicio, fim)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
