#!/usr/bin/env python3
"""
Atualização de marcos e status dos processos rastreados no caminho Pregão
(CLAUDE.md, seções 3 e 8).

Para cada processo em data/processos.json com caminho == "pregao" e fase !=
"Homologado" (estado terminal, não precisa mais de atualização — seção 8):
re-busca a página do processo (usando o processo_id já conhecido, nunca
busca por número — ver limitação documentada no CLAUDE.md seção 12),
recalcula a sub-etapa atual e os marcos de data a partir dos documentos, e
detecta os estados especiais (Homologado / Em recurso / Suspenso).

Limitação assumida: o resumo em texto livre "situação atual" (CLAUDE.md
seção 9) normalmente é escrito por uma sessão do Claude lendo o processo com
juízo humano — este script gera só um resumo mecânico (último documento +
última movimentação), sem prosa. Uma sessão do Claude pode revisar/reescrever
esse campo à mão quando quiser mais qualidade.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_documentos, extrair_movimentacoes  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
PROCESSOS_PATH = REPO_ROOT / "data" / "processos.json"

# Sub-etapas do caminho Pregão (CLAUDE.md seção 3), separadas por
# processo-fonte — DFD/ETP/TR/Lista SÓ podem vir do processo de
# Planejamento; as demais SÓ do processo de Pregão. Nunca misturar (regra
# explícita do CLAUDE.md seção 2) — já causou um bug real nesta automação
# (um processo já em Fase Externa foi rebaixado de volta pra "dfd" porque
# o script leu o processo de Pregão, que naturalmente não tem os documentos
# de DFD/ETP/TR — esses só existem no apenso de Planejamento).
SUBETAPAS_PLANEJAMENTO = [
    ("dfd", ["AUTORIZAÇÃO DA FORMALIZAÇÃO DE DEMANDA"]),
    ("etp", ["AUTORIZAÇÃO DOS ESTUDOS TÉCNICOS"]),
    ("tr", ["AUTORIZAÇÃO DO TERMO DE REFERÊNCIA"]),
    ("lista", ["LISTA DE VERIFICAÇÃO"]),  # fim real = movimentação p/ DFI, tratado à parte
]
SUBETAPAS_PREGAO = [
    ("analiseDfi", ["NOTA INFORMATIVA.*PESQUISA DE PRE"]),
    ("pesquisaPrecos", ["NOTA INFORMATIVA.*INTEN[ÇC][ÃA]O DE REGISTRO"]),
    ("irp", ["NOTA INFORMATIVA.*ELABORA[ÇC][ÃA]O DE EDITAL"]),
    ("edital", ["CERTIFICA[ÇC][ÃA]O PROCESSUAL"]),
    ("juridico", ["AN[ÁA]LISE DE PARECER JUR[ÍI]DICO"]),
    ("dfe", ["HOMOLOGA[ÇC][ÃA]O"]),
]
ORDEM_GLOBAL = ["dfd", "etp", "tr", "lista", "analiseDfi", "pesquisaPrecos", "irp", "edital", "juridico", "dfe"]

FASE_POR_SUBETAPA = {
    "dfd": "Planejamento (DPGC)",
    "etp": "Planejamento (DPGC)",
    "tr": "Planejamento (DPGC)",
    "lista": "Planejamento (DPGC)",
    "analiseDfi": "Fase Interna (DFI)",
    "pesquisaPrecos": "Fase Interna (DFI)",
    "irp": "Fase Interna (DFI)",
    "edital": "Fase Interna (DFI)",
    "juridico": "Jurídico (Projur/Análise)",
    "dfe": "Fase Externa (DFE)",
}
MARCO_FIM_POR_SUBETAPA = {
    "dfd": "dfdFim",
    "etp": "etpFim",
    "tr": "trFim",
    "lista": "listaFim",
    "analiseDfi": "analiseDfiFim",
    "pesquisaPrecos": "pesquisaPrecosFim",
    "irp": "irpFim",
    "edital": "editalFim",
    "juridico": "juridicoFim",
    "dfe": "dfeFim",
}

import re as _re


def _match_any(tipo: str, padroes: list[str]) -> bool:
    return any(_re.search(p, tipo, _re.IGNORECASE) for p in padroes)


def calcular_progresso(docs, etapas: list[tuple[str, list[str]]]) -> tuple[str | None, dict, bool]:
    """Varre os documentos em ordem e descobre até onde o processo avançou
    dentro de uma lista de etapas (sempre de UM processo-fonte só — nunca
    misturar planejamento com pregão, ver comentário acima).
    Retorna (subEtapa_atual, marcos, chegou_ao_fim_dessas_etapas)."""
    marcos = {}
    ultima_completada_idx = -1
    for i, (chave, padroes) in enumerate(etapas):
        doc_encontrado = next((d for d in docs if _match_any(d.tipo, padroes)), None)
        if doc_encontrado:
            marcos[MARCO_FIM_POR_SUBETAPA[chave]] = doc_encontrado.data
            ultima_completada_idx = i

    chegou_ao_fim = ultima_completada_idx == len(etapas) - 1
    if chegou_ao_fim:
        return None, marcos, True

    proxima_idx = ultima_completada_idx + 1
    sub_atual = etapas[proxima_idx][0] if proxima_idx < len(etapas) else None
    return sub_atual, marcos, False


def detectar_estados_especiais(docs, movimentacoes) -> dict:
    tipos = [d.tipo.upper() for d in docs]
    homologado = any("HOMOLOGA" in t for t in tipos)
    em_recurso = any("RECURSO ADMINISTRATIVO DE LICITA" in t for t in tipos) and any(
        "JULGAMENTO DE RECURSO" in t for t in tipos
    )
    # Suspenso: exige abrir o texto da movimentação DFE -> Diretoria de
    # Compras que não seja homologação nem recurso (CLAUDE.md seção 8).
    # Este script sinaliza o candidato; a leitura do texto fica para quem
    # revisar (não presumir suspensão só pela movimentação).
    candidato_suspensao = False
    for mv in movimentacoes:
        if "DIRETORIA DE COMPRAS" in mv.unidade_destino.upper() and "DFE" in mv.unidade_origem.upper():
            if not homologado and not em_recurso:
                candidato_suspensao = True
    return {
        "homologado": homologado,
        "em_recurso": em_recurso,
        "candidato_suspensao": candidato_suspensao,
    }


def resumo_mecanico(docs, movimentacoes) -> str:
    partes = []
    if docs:
        ultimo = docs[-1]
        partes.append(f"Último documento: {ultimo.tipo} ({ultimo.data})")
    if movimentacoes:
        m = movimentacoes[-1]
        partes.append(f"Última movimentação: {m.unidade_origem} → {m.unidade_destino} ({m.data_origem})")
    return " · ".join(partes) if partes else "Sem documentos ou movimentações registradas ainda."


def atualizar_todos() -> dict:
    data = json.loads(PROCESSOS_PATH.read_text(encoding="utf-8"))
    client = SipacClient()

    atualizados = 0
    avisos = []

    for p in data:
        if p.get("caminho") != "pregao" or p.get("fase") == "Homologado":
            continue

        tem_pregao_vinculado = bool(p.get("pregao"))
        mudou = False
        subetapa_mudou = False

        if tem_pregao_vinculado:
            # Já apensou/formalizou o pregão: DFD/ETP/TR/Lista são história
            # do apenso de planejamento (id ainda não resolvido para todos os
            # processos antigos — ver aviso abaixo) e não são recalculados
            # aqui. Só a parte do processo de PREGÃO é reavaliada.
            if not p.get("pregao_id"):
                avisos.append(
                    f"{p['processo']}: tem pregão vinculado ({p['pregao']}) mas o id interno do "
                    f"SIPAC do pregão não está resolvido — pulado nesta execução. Resolver via "
                    f"cross-referência (busca por tipo 1470 na janela de datas prováveis)."
                )
                continue
            html = client.obter_processo(p["pregao_id"])
            docs = extrair_documentos(html)
            movs = extrair_movimentacoes(html)
            etapas = SUBETAPAS_PREGAO
        else:
            if not p.get("processo_id"):
                avisos.append(f"{p['processo']}: sem processo_id resolvido — pulado.")
                continue
            html = client.obter_processo(p["processo_id"])
            docs = extrair_documentos(html)
            movs = extrair_movimentacoes(html)
            etapas = SUBETAPAS_PLANEJAMENTO

        sub_atual, marcos_novos, _chegou_ao_fim = calcular_progresso(docs, etapas)
        estados = detectar_estados_especiais(docs, movs)

        if estados["homologado"] and p.get("fase") != "Homologado":
            p["fase"] = "Homologado"
            p["subEtapa"] = None
            mudou = subetapa_mudou = True
        elif sub_atual and sub_atual != p.get("subEtapa"):
            # Nunca deixa a atualização automática RETROCEDER a sub-etapa.
            # Alguns processos rotulam o despacho de autorização de forma
            # genérica ("DESPACHO" sem tipo específico), o que faz o
            # casamento por palavra-chave falhar silenciosamente e pareceria
            # um retrocesso — mais seguro não aplicar do que corromper um
            # dado que já foi lido/confirmado com juízo humano antes.
            idx_novo = ORDEM_GLOBAL.index(sub_atual) if sub_atual in ORDEM_GLOBAL else -1
            idx_atual = ORDEM_GLOBAL.index(p["subEtapa"]) if p.get("subEtapa") in ORDEM_GLOBAL else -1
            if idx_novo > idx_atual:
                p["subEtapa"] = sub_atual
                p["fase"] = FASE_POR_SUBETAPA[sub_atual]
                mudou = subetapa_mudou = True
            elif idx_novo < idx_atual:
                avisos.append(
                    f"{p['processo']}: a extração automática calculou a sub-etapa '{sub_atual}', "
                    f"anterior à registrada ('{p['subEtapa']}') — provável documento de "
                    f"autorização rotulado de forma genérica no SIPAC (ex. 'DESPACHO' sem tipo "
                    f"específico). Sub-etapa NÃO alterada; conferir manualmente se quiser."
                )

        if estados["em_recurso"] != p.get("emRecurso", False):
            p["emRecurso"] = estados["em_recurso"]
            mudou = True

        if estados["candidato_suspensao"] and not p.get("suspenso"):
            avisos.append(
                f"{p['processo']}: movimentação DFE→Diretoria de Compras que não é "
                f"homologação nem recurso — abrir o documento e confirmar suspensão manualmente "
                f"(CLAUDE.md seção 8). NÃO marcado automaticamente."
            )

        marcos_existentes = p.get("marcos") or {}
        marcos_combinados = {**marcos_existentes, **marcos_novos}
        if marcos_combinados != marcos_existentes:
            p["marcos"] = marcos_combinados
            mudou = True

        # Só sobrescreve o texto de "situação atual" quando ele ficaria
        # desatualizado de verdade (mudou de sub-etapa) ou nunca existiu —
        # texto escrito à mão (por uma sessão do Claude lendo com juízo)
        # é sempre mais rico que o resumo mecânico e não deve ser perdido
        # à toa a cada execução automática.
        if subetapa_mudou or not p.get("subetapa"):
            novo_resumo = resumo_mecanico(docs, movs)
            if novo_resumo != p.get("subetapa"):
                p["subetapa"] = novo_resumo
                mudou = True

        # Planejamento que já foi enviado à DFI mas ainda não tem o número
        # do pregão vinculado — não dá para descobrir automaticamente
        # (busca por número não funciona); sinaliza para confirmação manual.
        if not tem_pregao_vinculado:
            enviado_a_dfi = any(
                "DFI" in mv.unidade_destino.upper() and "PLANEJAMENTO" not in mv.unidade_destino.upper()
                for mv in movs
            )
            if enviado_a_dfi:
                avisos.append(
                    f"{p['processo']}: processo foi enviado à DFI mas ainda não tem número de "
                    f"pregão vinculado no painel — confirmar manualmente (busca por número não "
                    f"funciona via automação, ver CLAUDE.md seção 12)."
                )

        if mudou:
            atualizados += 1

    PROCESSOS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"processos_verificados": sum(1 for p in data if p.get("caminho") == "pregao"), "atualizados": atualizados, "avisos": avisos}


if __name__ == "__main__":
    resumo = atualizar_todos()
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
