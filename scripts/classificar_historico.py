#!/usr/bin/env python3
"""
Classifica em massa o caminho de cada processo de Planejamento descoberto
pela varredura histórica (data/processos_index_cache.json), cruzando com o
mapeamento de apensações (data/apensacoes_cache.json).

Regra de decisão, por processo de planejamento ainda não rastreado (nem em
data/processos.json nem em data/portao_pendentes.json, checado por número):

  1. Não achou apensação para esse número → fila do portão (pendente).
  2. Achou apensação, e o número do processo de execução bate em EXATAMENTE
     um dos 5 índices por tipo (pregao/dispensa/inexigibilidade/adesao_srp/
     concorrencia) → classificação confiante, entra direto em processos.json
     (marcos ainda vazios — scripts/atualizar_marcos.py preenche depois).
  3. Achou apensação mas o número do processo de execução não bate em
     nenhum tipo, ou bate em mais de um (não deveria acontecer, mas por
     segurança) → ambíguo, fila do portão com uma nota do problema.

Formato de entrada em processos.json: mesmo usado em aplicar_decisoes.py,
adaptado por caminho (ver comentários em atualizar_marcos.py sobre quais
campos cada caminho usa: pregao/execucao_numero+execucao_id vs processo_id
direto pra adesao_srp/concorrencia).

Uso:
    python3 scripts/classificar_historico.py [--limite N] [--dry-run]

--limite N: processa só os N primeiros planejamentos ainda não rastreados
  (pra testar em amostra pequena antes de rodar tudo).
--dry-run: não escreve nada, só imprime o que faria.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
PROCESSOS_PATH = DATA_DIR / "processos.json"
PENDENTES_PATH = DATA_DIR / "portao_pendentes.json"
APENSACOES_PATH = DATA_DIR / "apensacoes_cache.json"
INDEX_PATH = DATA_DIR / "processos_index_cache.json"

EXECUCAO_TIPOS = ["pregao", "dispensa", "inexigibilidade", "adesao_srp", "concorrencia"]

# Sub-etapa mais cedo de cada caminho — ponto de partida seguro pra
# atualizar_marcos.py avançar livremente sem esbarrar na trava de
# "nunca retroceder automaticamente" (ver atualizar_marcos.py).
SUBETAPA_INICIAL = {
    "pregao": "dfd",
    "dispensa": "planejamento",
    "inexigibilidade": "planejamento",
    "adesao_srp": "planejamento",
    "concorrencia": "faseExterna",
}
FASE_INICIAL = {
    "pregao": "Planejamento (DPGC)",
    "dispensa": "Planejamento (DPGC)",
    "inexigibilidade": "Planejamento (DPGC)",
    "adesao_srp": "Planejamento (DPGC)",
    "concorrencia": "Fase Externa (DFE)",
}

LINK_BASE = "https://sipac.ufrn.br/public/jsp/processos/processo_detalhado.jsf?id="


def carregar_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def salvar_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def montar_entrada_confiante(numero_planejamento: str, info_planejamento: dict, caminho: str, execucao_numero: str, info_execucao: dict, hoje_iso: str) -> dict:
    subetapa_inicial = SUBETAPA_INICIAL[caminho]
    fase_inicial = FASE_INICIAL[caminho]
    nota = "Adicionado via levantamento histórico — aguardando a próxima atualização automática de marcos."

    entrada = {
        "processo": numero_planejamento,
        "assunto": info_planejamento.get("assunto", ""),
        "fase": fase_inicial,
        "subEtapa": subetapa_inicial,
        "subetapa": nota,
        "categoria": "elaboracao",
        "unidade": "",
        "data": hoje_iso,
        "dataCriacao": hoje_iso,
        "gestor": None,
        "suspenso": False,
        "emRecurso": False,
        "urgente": False,
        "marcos": None,
        "caminho": caminho,
        "caminhoHistorico": [],
    }

    if caminho == "pregao":
        entrada["pregao"] = execucao_numero
        entrada["pregao_id"] = info_execucao["id"]
        entrada["processo_id"] = None
        entrada["link"] = LINK_BASE + str(info_execucao["id"])
    elif caminho in ("dispensa", "inexigibilidade"):
        entrada["execucao_numero"] = execucao_numero
        entrada["execucao_id"] = info_execucao["id"]
        entrada["processo_id"] = None
        entrada["link"] = LINK_BASE + str(info_execucao["id"])
    elif caminho == "adesao_srp":
        # Lê sempre do processo de Planejamento (docs reais vivem lá) —
        # ver comentário em atualizar_marcos.py sobre SEMPRE_PROCESSO_ID.
        entrada["processo_id"] = info_planejamento["id"]
        entrada["link"] = LINK_BASE + str(info_planejamento["id"])
    elif caminho == "concorrencia":
        # Inverso do adesao_srp: o planejamento apensado é ignorado (ou é
        # só a hipótese de planejamento embrionário, seção 4.4 do
        # CLAUDE.md) — os documentos reais (Fase Externa/Homologação)
        # vivem no processo de Concorrência em si.
        entrada["processo_id"] = info_execucao["id"]
        entrada["link"] = LINK_BASE + str(info_execucao["id"])

    return entrada


def montar_entrada_pendente(numero_planejamento: str, info_planejamento: dict, hoje_iso: str, motivo: str) -> dict:
    return {
        "processo_id": info_planejamento["id"],
        "numero": numero_planejamento,
        "assunto": info_planejamento.get("assunto", ""),
        "primeiro_documento": None,
        "status": "pendente",
        "link": LINK_BASE + str(info_planejamento["id"]),
        "descoberto_em": hoje_iso,
        "nota_classificacao": motivo,
    }


def classificar(limite: int | None, dry_run: bool) -> dict:
    apensacoes = carregar_json(APENSACOES_PATH, {}).get("apensacoes", {})
    idx = carregar_json(INDEX_PATH, {})
    planejamentos = idx.get("planejamento", {}).get("processos", {})

    processos = carregar_json(PROCESSOS_PATH, [])
    pendentes = carregar_json(PENDENTES_PATH, [])

    numeros_ja_processos = {p["processo"] for p in processos}
    numeros_ja_pendentes = {p["numero"] for p in pendentes}

    hoje_iso = date.today().strftime("%d/%m/%Y")

    novos_processos = []
    novos_pendentes = []
    contagem_por_caminho: dict[str, int] = {}
    processados = 0

    for numero, info_planejamento in planejamentos.items():
        if numero in numeros_ja_processos or numero in numeros_ja_pendentes:
            continue
        if limite is not None and processados >= limite:
            break
        processados += 1

        apensacao = apensacoes.get(numero)
        if not apensacao:
            novos_pendentes.append(
                montar_entrada_pendente(numero, info_planejamento, hoje_iso, "sem apensação encontrada na varredura 2024-hoje")
            )
            continue

        execucao_numero = apensacao["execucao_numero"]
        matches = [t for t in EXECUCAO_TIPOS if execucao_numero in idx.get(t, {}).get("processos", {})]

        if len(matches) == 1:
            caminho = matches[0]
            info_execucao = idx[caminho]["processos"][execucao_numero]
            entrada = montar_entrada_confiante(numero, info_planejamento, caminho, execucao_numero, info_execucao, hoje_iso)
            novos_processos.append(entrada)
            contagem_por_caminho[caminho] = contagem_por_caminho.get(caminho, 0) + 1
        else:
            motivo = (
                f"apensado a {execucao_numero}, mas esse número não foi encontrado em nenhum dos 5 tipos de execução"
                if not matches
                else f"apensado a {execucao_numero}, que bateu em mais de um tipo de execução: {matches}"
            )
            novos_pendentes.append(montar_entrada_pendente(numero, info_planejamento, hoje_iso, motivo))

    if not dry_run:
        processos.extend(novos_processos)
        pendentes.extend(novos_pendentes)
        salvar_json(PROCESSOS_PATH, processos)
        salvar_json(PENDENTES_PATH, pendentes)

    return {
        "processados_nesta_execucao": processados,
        "confiantes_adicionados_a_processos_json": len(novos_processos),
        "por_caminho": contagem_por_caminho,
        "enviados_ao_portao": len(novos_pendentes),
        "dry_run": dry_run,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    resumo = classificar(args.limite, args.dry_run)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
