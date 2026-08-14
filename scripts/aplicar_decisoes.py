#!/usr/bin/env python3
"""
Aplica decisões tomadas na tela do portão de entrada (Acompanhar/Ignorar)
de volta aos dados reais do painel.

O front-end (docs/index.html) é uma página estática — não escreve no
repositório sozinha. Decisões ficam guardadas no navegador (localStorage)
até a pessoa copiar o bloco JSON exibido em "Copiar decisões" e colar numa
conversa com o Claude, que roda este script e commita o resultado.

Uso:
    python3 scripts/aplicar_decisoes.py decisoes.json
    # ou via stdin:
    echo '[{"processo_id":123,"decisao":"acompanhar","caminho":"pregao"}]' | python3 scripts/aplicar_decisoes.py -

Formato de cada decisão: {"processo_id": int, "decisao": "acompanhar"|"ignorar", "caminho": str|null}
"caminho" só é obrigatório quando decisao == "acompanhar".
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PENDENTES_PATH = REPO_ROOT / "data" / "portao_pendentes.json"
PROCESSOS_PATH = REPO_ROOT / "data" / "processos.json"
IGNORADOS_PATH = REPO_ROOT / "data" / "ignorados.json"

CAMINHOS_VALIDOS = {"pregao", "dispensa", "inexigibilidade", "adesao_srp", "concorrencia", "contratabrasil"}

# Primeira sub-etapa de cada caminho, na nomenclatura real que
# scripts/atualizar_marcos.py usa (ORDEM_* daquele arquivo) — tem que bater
# exatamente com as chaves de CAMINHOS[...].etapas em docs/index.html, senão
# a trilha desses processos recém-adicionados nasce quebrada (mesmo bug já
# corrigido pra quem já estava em processos.json). "concorrencia" e
# "contratabrasil" não nascem como Planejamento (33.00) apensado no modelo
# atual (CLAUDE.md seção 4.4/4.5) — escolher esses caminhos pra um processo
# vindo do portão é caso fora do padrão; fica sem sub-etapa inicial definida
# pra não presumir.
PRIMEIRA_SUBETAPA = {
    "pregao": "dfd",
    "dispensa": "planejamento",
    "inexigibilidade": "planejamento",
    "adesao_srp": "planejamento",
}


def aplicar(decisoes: list[dict]) -> dict:
    pendentes = json.loads(PENDENTES_PATH.read_text(encoding="utf-8"))
    processos = json.loads(PROCESSOS_PATH.read_text(encoding="utf-8"))
    ignorados_registro = json.loads(IGNORADOS_PATH.read_text(encoding="utf-8")) if IGNORADOS_PATH.exists() else []

    pendentes_por_id = {p["processo_id"]: p for p in pendentes}
    acompanhados, ignorados, nao_encontrados = [], [], []
    hoje_iso = date.today().strftime("%d/%m/%Y")

    for d in decisoes:
        pid = d["processo_id"]
        acao = d["decisao"]
        pendente = pendentes_por_id.get(pid)
        if pendente is None:
            nao_encontrados.append(pid)
            continue

        if acao == "acompanhar":
            caminho = d.get("caminho")
            if caminho not in CAMINHOS_VALIDOS:
                raise ValueError(f"processo_id {pid}: caminho inválido ou ausente: {caminho!r}")
            processos.append(
                {
                    "processo": pendente["numero"],
                    "assunto": pendente.get("assunto", ""),
                    "fase": "Planejamento (DPGC)",
                    "subEtapa": PRIMEIRA_SUBETAPA.get(caminho),
                    "subetapa": "Adicionado via portão de entrada — aguardando a próxima atualização automática de marcos.",
                    "categoria": "elaboracao",
                    "unidade": "",
                    "data": pendente.get("descoberto_em", ""),
                    "dataCriacao": pendente.get("descoberto_em", ""),
                    "gestor": None,
                    "pregao": None,
                    "suspenso": False,
                    "emRecurso": False,
                    "urgente": False,
                    "link": pendente.get("link", ""),
                    "marcos": None,
                    "caminho": caminho,
                    "caminhoHistorico": [],
                    "processo_id": pid,
                    "pregao_id": None,
                }
            )
            acompanhados.append(pendente["numero"])
        elif acao == "ignorar":
            ignorados.append(pendente["numero"])
            # Guarda o registro em vez de só descartar — permite que
            # scripts/revisar_ignorados.py detecte depois se o processo
            # voltou a se movimentar e o traga de volta pro portão (pedido
            # explícito da pessoa dona do projeto: "ignorar" não devia ser
            # definitivo se o processo criar vida de novo).
            ignorados_registro.append(
                {
                    "processo_id": pid,
                    "numero": pendente["numero"],
                    "assunto": pendente.get("assunto", ""),
                    "link": pendente.get("link", ""),
                    "ignoradoEm": hoje_iso,
                    "ultimaAtividadeNoIgnorar": pendente.get("ultimaAtividade"),
                    "motivo": d.get("motivo"),
                }
            )
        else:
            raise ValueError(f"processo_id {pid}: decisão desconhecida: {acao!r}")

        del pendentes_por_id[pid]

    pendentes_restantes = list(pendentes_por_id.values())

    PENDENTES_PATH.write_text(json.dumps(pendentes_restantes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PROCESSOS_PATH.write_text(json.dumps(processos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IGNORADOS_PATH.write_text(json.dumps(ignorados_registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "acompanhados": acompanhados,
        "ignorados": ignorados,
        "nao_encontrados_na_fila": nao_encontrados,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python3 scripts/aplicar_decisoes.py <arquivo.json|->", file=sys.stderr)
        sys.exit(1)
    origem = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text(encoding="utf-8")
    resultado = aplicar(json.loads(origem))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
