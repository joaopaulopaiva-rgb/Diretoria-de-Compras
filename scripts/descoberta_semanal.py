#!/usr/bin/env python3
"""
Descoberta automática de processos novos de Planejamento (CLAUDE.md, seção 11).

Roda toda sexta-feira (via GitHub Actions) e sob demanda. Busca processos do
tipo PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO (33.00) cadastrados nos últimos 7
dias e ignora os já vistos.

Decisão de validação (revista empiricamente — "1º documento = DFD Digital"
quase nunca bate literalmente na prática, a maioria dos processos tem um
Ofício ou Protocolo antes do DFD): a descoberta NÃO tenta mais classificar
padrão/exceção sozinha. Todo processo novo entra na fila do portão com
status "pendente", e a pessoa decide na tela: ACOMPANHAR (pergunta o
caminho: pregão/dispensa/inexigibilidade/adesão_srp/concorrência/
contrata+brasil), IGNORAR, ou EM_ANALISE (continua aparecendo até virar
uma das duas decisões acima).

Saída:
  - data/portao_pendentes.json: fila de processos novos para a pessoa
    revisar na tela do "portão de entrada".
  - data/vistos.json: cache de processos já processados, para não reabrir.
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, TIPO_PROCESSO, extrair_documentos, extrair_num_registros_encontrados  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
VISTOS_PATH = DATA_DIR / "vistos.json"
PENDENTES_PATH = DATA_DIR / "portao_pendentes.json"

DOC_GATILHO_PADRAO = "DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA DIGITAL (DFD DIGITAL)"
STATUS_PENDENTE = "pendente"


def carregar_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def salvar_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def buscar_com_janela_adaptativa(client: SipacClient, tipo_value: int, inicio: date, fim: date):
    """Busca processos por tipo no período dado. Se o nº de registros
    encontrados exceder o que a página mostra (truncamento conhecido do
    SIPAC — ver CLAUDE.md seção 12), divide a janela ao meio recursivamente."""
    resultados = client.buscar_processos_por_tipo(tipo_value, inicio, fim)
    if inicio >= fim:
        return resultados
    meio = inicio + (fim - inicio) // 2
    if meio == inicio:
        return resultados
    # Heurística: se a página devolveu o teto de truncamento observado
    # empiricamente (15), reconsulta em duas metades para não perder registros.
    if len(resultados) >= 15:
        parte1 = buscar_com_janela_adaptativa(client, tipo_value, inicio, meio)
        parte2 = buscar_com_janela_adaptativa(client, tipo_value, meio + timedelta(days=1), fim)
        vistos_ids = {r.processo_id for r in parte1}
        combinado = parte1 + [r for r in parte2 if r.processo_id not in vistos_ids]
        return combinado
    return resultados


def descobrir(dias_janela: int = 7, hoje: date | None = None) -> dict:
    hoje = hoje or date.today()
    inicio = hoje - timedelta(days=dias_janela)

    client = SipacClient()
    vistos = set(carregar_json(VISTOS_PATH, []))
    pendentes = carregar_json(PENDENTES_PATH, [])
    pendentes_ids = {p["processo_id"] for p in pendentes}

    resultados = buscar_com_janela_adaptativa(client, TIPO_PROCESSO["planejamento"], inicio, hoje)

    novos = []
    for r in resultados:
        if r.processo_id in vistos or r.processo_id in pendentes_ids:
            continue

        html_processo = client.obter_processo(r.processo_id)
        docs = extrair_documentos(html_processo)
        primeiro_doc = docs[0].tipo if docs else None

        entrada = {
            "processo_id": r.processo_id,
            "numero": r.numero,
            "assunto": r.assunto,
            "primeiro_documento": primeiro_doc,  # informativo, não filtra mais
            "status": STATUS_PENDENTE,
            "link": f"https://sipac.ufrn.br/public/jsp/processos/processo_detalhado.jsf?id={r.processo_id}",
            "descoberto_em": hoje.isoformat(),
        }
        vistos.add(r.processo_id)
        novos.append(entrada)

    pendentes.extend(novos)

    salvar_json(VISTOS_PATH, sorted(vistos))
    salvar_json(PENDENTES_PATH, pendentes)

    return {
        "janela": {"inicio": inicio.isoformat(), "fim": hoje.isoformat()},
        "total_encontrados_na_busca": len(resultados),
        "novos_na_fila_do_portao": len(novos),
        "ja_vistos_ou_na_fila": len(resultados) - len(novos),
    }


if __name__ == "__main__":
    resumo = descobrir()
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
