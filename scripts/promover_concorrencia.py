#!/usr/bin/env python3
"""
Promove processos de Concorrência (tipo=220) já descobertos no índice bruto
(data/processos_index_cache.json['concorrencia']) pra data/processos.json.

Por que existe um script separado só pra Concorrência: nos outros caminhos
(Pregão/Dispensa/Inexigibilidade/Adesão SRP), a descoberta acontece a
partir de um processo de Planejamento (33.00) apensado — scripts/
classificar_historico.py e o portão cobrem isso. Concorrência é diferente
(CLAUDE.md seção 4.4): na maioria dos casos (14/16 confirmados por auditoria
anterior) ela NÃO apensa um processo de Planejamento separado — nasce e
tramita inteira dentro do próprio número, na CAOSE/INFRA. Não existe
"processo de planejamento" pra apensar e disparar a descoberta pelos
caminhos normais — por isso os processos de Concorrência reais ficavam
presos no índice bruto, nunca promovidos.

Filtra ruído (a busca por tipo=220 traz ~58% de processos acessórios de
gestão contratual pós-obra — aditivo, reequilíbrio, reajuste — CLAUDE.md
seção 4.4): só promove processos cujo "Assunto Detalhado" comece com
"CONCORRÊNCIA" de verdade.

Fase inicial: usa a mesma constante FASE_CONCORRENCIA_PRE_DFE que
scripts/atualizar_marcos.py usa (literal duplicado de propósito, mesmo
motivo do PLACEHOLDER_SUBETAPA) — deixa a filtragem correta (não é
"Planejamento (DPGC)" de verdade, é CAOSE/INFRA) pra próxima rodada de
atualizar_marcos.py confirmar/avançar com evidência real de documentos.

Uso:
    python3 scripts/promover_concorrencia.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
PROCESSOS_PATH = DATA_DIR / "processos.json"
INDEX_PATH = DATA_DIR / "processos_index_cache.json"

LINK_BASE = "https://sipac.ufrn.br/public/jsp/processos/processo_detalhado.jsf?id="

# Mesmos literais usados em scripts/atualizar_marcos.py / aplicar_decisoes.py.
PLACEHOLDER_SUBETAPA = "Adicionado via portão de entrada — aguardando a próxima atualização automática de marcos."
FASE_CONCORRENCIA_PRE_DFE = "Concorrência · aguardando Fase Externa (CAOSE/INFRA)"

_ASSUNTO_CONCORRENCIA_RE = re.compile(r"^CONCORR[ÊE]NCIA\b", re.IGNORECASE)


def promover(dry_run: bool) -> dict:
    idx = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    concorrencia_idx = idx.get("concorrencia", {}).get("processos", {})

    processos = json.loads(PROCESSOS_PATH.read_text(encoding="utf-8"))
    numeros_ja_rastreados = {p["processo"] for p in processos}

    hoje_iso = date.today().strftime("%d/%m/%Y")
    promovidos = []
    ja_rastreados = []
    descartados_ruido = []

    for numero, info in concorrencia_idx.items():
        assunto = info.get("assunto", "").strip()
        if not _ASSUNTO_CONCORRENCIA_RE.match(assunto):
            descartados_ruido.append(numero)
            continue
        if numero in numeros_ja_rastreados:
            ja_rastreados.append(numero)
            continue

        processos.append(
            {
                "processo": numero,
                "assunto": assunto,
                "fase": FASE_CONCORRENCIA_PRE_DFE,
                "subEtapa": None,
                "subetapa": PLACEHOLDER_SUBETAPA,
                "categoria": "elaboracao",
                "unidade": "",
                "data": hoje_iso,
                "dataCriacao": hoje_iso,
                "gestor": None,
                "suspenso": False,
                "emRecurso": False,
                "urgente": False,
                "marcos": None,
                "caminho": "concorrencia",
                "caminhoHistorico": [],
                "processo_id": info["id"],
                "link": LINK_BASE + str(info["id"]),
            }
        )
        promovidos.append(numero)

    if not dry_run and promovidos:
        PROCESSOS_PATH.write_text(json.dumps(processos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "total_no_indice": len(concorrencia_idx),
        "descartados_ruido": len(descartados_ruido),
        "ja_rastreados": ja_rastreados,
        "promovidos": promovidos,
        "total_promovidos": len(promovidos),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    resumo = promover(args.dry_run)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
