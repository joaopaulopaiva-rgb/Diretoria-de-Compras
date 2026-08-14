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
from sipac_client import SipacClient, extrair_documentos, extrair_movimentacoes, texto_visivel  # noqa: E402

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

# --- Dispensa de Licitação ---
# Modelo enxuto definido pela pessoa dona do projeto (não usa a tabela
# detalhada do CLAUDE.md seção 4.1 — foi simplificado de propósito), validado
# contra 3 processos reais: 2 "com disputa de fase externa" e 1 "sem disputa"
# (23077.117430/2026-19, DL 90034/2026).
#
# Só 1 etapa lida do processo de Planejamento apensado:
#   Planejamento: da criação até "Autorização de Formalização - Contratação
#   Direta" (mesma regra de nunca misturar fonte, CLAUDE.md seção 2).
#
# As etapas seguintes são detectadas pela ORIGEM de cada documento no
# processo de Dispensa (não pelo tipo do documento nem pela tabela de
# "Movimentações", que fica praticamente vazia nesses processos) — a
# tramitação real fica registrada em qual unidade *emitiu* cada documento:
#   Fase Interna: enquanto os documentos continuam saindo da DFI.
#   Fase Externa: a partir do primeiro documento com origem DFE — só
#     acontece se houve disputa. Detectado também pelo "Relatório de
#     Julgamento de Propostas": se sai da DFE, teve disputa; se sai da
#     própria DFI, não teve (pula direto pra Homologado).
#   Homologado: a partir do primeiro documento com origem no DCF (ex.
#     "SEO/DCF/PROAD") — regra confirmada pela pessoa dona do projeto:
#     "se teve movimentação depois que o processo passou pela DFE indo pro
#     DCF, pode considerar que foi encerrado" (vale igual pro caminho sem
#     disputa, que vai direto de DFI pro DCF).
SUBETAPAS_PLANEJAMENTO_DISPENSA = [
    ("planejamento", ["AUTORIZA[ÇC][ÃA]O DE FORMALIZA[ÇC][ÃA]O.*CONTRATA[ÇC][ÃA]O DIRETA"]),
]
ORDEM_DISPENSA = ["planejamento", "faseInterna", "faseExterna"]


def calcular_progresso_dispensa_execucao(docs) -> tuple[str | None, dict, bool, bool | None]:
    """Calcula a sub-etapa dentro do processo de Dispensa (pós-planejamento)
    a partir da ORIGEM dos documentos, não do tipo. Retorna (subEtapa,
    marcos, concluido, sem_disputa_fase_externa — None se ainda não dá pra
    saber)."""
    marcos: dict = {}
    sem_disputa: bool | None = None

    julgamento = next((d for d in docs if "JULGAMENTO DE PROPOSTAS" in d.tipo.upper()), None)
    if julgamento:
        sem_disputa = "DFE" not in julgamento.origem.upper()

    doc_dfe = next((d for d in docs if "DFE" in d.origem.upper()), None)
    sub_atual = "faseInterna"
    if doc_dfe:
        marcos["faseExternaInicio"] = doc_dfe.data
        sub_atual = "faseExterna"
        sem_disputa = False

    doc_dcf = next((d for d in docs if "DCF" in d.origem.upper()), None)
    concluido = doc_dcf is not None
    if concluido:
        marcos["homologadoData"] = doc_dcf.data
        sub_atual = None

    return sub_atual, marcos, concluido, sem_disputa


# --- Inexigibilidade de Licitação ---
# Mesmo modelo por origem da Dispensa, mas mais simples: nunca tem Fase
# Externa (CLAUDE.md seção 4.2 já indicava "sem DFE"; confirmado em 2
# processos reais — "Relatório de Julgamento de Propostas" sempre sai da
# própria DFI, nunca da DFE). Nem sempre passa pelo DCF: alguns processos
# formalizam por Contrato (setor Contratos/PROAD) em vez de só Empenho.
# Regra confirmada pela pessoa dona do projeto: "quando sair da Diretoria de
# Compras pra PROAD ou DCF, pode considerar Homologado" — importante: essa
# regra NÃO se aplica à Dispensa (lá "PROAD" sozinho aparece cedo, na
# checagem de orçamento, e marcaria conclusão errada demais cedo).
SUBETAPAS_PLANEJAMENTO_INEXIGIBILIDADE = [
    ("planejamento", ["AUTORIZA[ÇC][ÃA]O DE FORMALIZA[ÇC][ÃA]O.*CONTRATA[ÇC][ÃA]O DIRETA"]),
]
ORDEM_INEXIGIBILIDADE = ["planejamento", "faseInterna"]


# --- Adesão a Ata de Registro de Preços (SRP) ---
# O mais simples de todos: as duas etapas rastreadas vivem inteiras dentro
# do próprio processo de Planejamento — confirmado em 2 processos reais, o
# invólucro tipo=258 que recebe a apensação tem pouquíssimo conteúdo próprio
# (só Termo de Juntada + Lista de Verificação). Por isso não precisa de
# processo de execução separado: sempre lê do processo de Planejamento
# (processo_id), nunca do "execucao_id".
#   Planejamento: da capa do processo até "Autorização de Formalização -
#     Adesão a Ata de Registro de Preços" (ainda na DPGC).
#   Fase Interna: até "Autorização de Adesão a Ata de Registro de Preços"
#     (na DFI) — esse é o fechamento real; a partir daí já é Homologado.
#     Execução (pedidos de material usando a ata) fica fora do escopo,
#     conforme já definido.
SUBETAPAS_ADESAO_SRP = [
    ("planejamento", ["AUTORIZA[ÇC][ÃA]O DE FORMALIZA[ÇC][ÃA]O.*ADES[ÃA]O"]),
    ("faseInterna", ["AUTORIZA[ÇC][ÃA]O DE ADES[ÃA]O A ATA"]),
]
ORDEM_ADESAO_SRP = ["planejamento", "faseInterna"]


# --- Concorrência ---
# Só cobre o caso confirmado em 10 processos reais (9 de 10 nascem na
# CAOSE/INFRA — obras): por orientação da pessoa dona do projeto,
# desconsidera todo o planejamento/tramitação da Infra (DFD/ETP/TR, mais de
# 100 documentos em processos típicos) — o acompanhamento começa quando o
# processo chega na Fase Externa (primeiro documento de origem DFE/COMPRAS,
# confirmado num processo real ativo, CC 90001/2026) e termina com
# "Homologação" (confirmado num processo real concluído, CC 4/2025: Termo
# de Julgamento + Homologação, mesmo padrão do Pregão — inclusive uma
# suspensão no meio do caminho que não impediu de chegar à Homologação).
# Os que nascem direto na Diretoria de Compras (minoria) ainda não têm
# tratamento definido.
SUBETAPAS_CONCORRENCIA = [
    ("faseExterna", ["HOMOLOGA[ÇC][ÃA]O"]),
]
ORDEM_CONCORRENCIA = ["faseExterna"]


# --- Concorrência que nasce na Diretoria de Compras (RASCUNHO, não validado) ---
# Caminho separado ("concorrencia_compras") pro caso minoritário em que a
# Concorrência nasce direto na Diretoria de Compras, não na CAOSE/INFRA —
# só examinamos 1 exemplo real até agora, e ele foi bem confuso (dois ciclos
# de DFD/ETP/TR quase um ano de diferença, apensação no meio, passagens por
# INFRA/STI/PoP-NRA sem padrão óbvio, nunca chegou na DFE). Não dá pra
# validar um padrão com 1 exemplo só — este desenho é uma primeira hipótese,
# copiada da estrutura do Pregão (mesmos documentos-gatilho, já que muitos
# batem com o que apareceu nesse exemplo), tudo lido de um processo só (sem
# separar planejamento/execução, já que aqui não houve apenso separado).
# Ajustar conforme mais processos reais desse tipo forem examinados.
SUBETAPAS_CONCORRENCIA_COMPRAS = [
    ("dfd", ["DOCUMENTO DE FORMALIZA[ÇC][ÃA]O DA DEMANDA DIGITAL"]),
    ("etp", ["AUTORIZA[ÇC][ÃA]O DOS ESTUDOS T[ÉE]CNICOS"]),
    ("tr", ["AUTORIZA[ÇC][ÃA]O DO TERMO DE REFER[ÊE]NCIA"]),
    ("edital", ["CERTIFICA[ÇC][ÃA]O PROCESSUAL"]),
    ("juridico", ["AN[ÁA]LISE DE PARECER JUR[ÍI]DICO"]),
    ("dfe", ["HOMOLOGA[ÇC][ÃA]O"]),
]
ORDEM_CONCORRENCIA_COMPRAS = ["dfd", "etp", "tr", "edital", "juridico", "dfe"]


def calcular_progresso_inexigibilidade_execucao(docs) -> tuple[str | None, dict, bool]:
    """Retorna (subEtapa, marcos, concluido) pro processo de Inexigibilidade
    (pós-planejamento), usando a origem dos documentos."""
    marcos: dict = {}
    sub_atual = "faseInterna"

    doc_conclusao = next(
        (d for d in docs if d.origem.strip().upper().startswith("PROAD (") or "DCF" in d.origem.upper()),
        None,
    )
    concluido = doc_conclusao is not None
    if concluido:
        marcos["homologadoData"] = doc_conclusao.data
        sub_atual = None

    return sub_atual, marcos, concluido


# --- Responsáveis na DFI e na DFE (só caminho Pregão) ---
# Pedido da pessoa dona do projeto: as 3 Notas Informativas da Fase Interna
# (Pesquisa de Preços, IRP, Elaboração de Edital) trazem o nome de quem é
# responsável por cada etapa dentro do texto do próprio documento — e o
# primeiro despacho que a DFE emite depois de receber o Encaminhamento da
# DFI designa o pregoeiro e a equipe de apoio. Padrões confirmados lendo
# documentos reais (agosto/2026):
#   Pesquisa de Preços — "Responsável pela pesquisa: NOME."
#   IRP                — "Responsável pela IRP: NOME"  (sem ponto final)
#   Elaboração de Edital — "Responsável pela instrução: NOME."
#   Despacho da DFE    — "... ao(à) agente de contratação NOME, que atuará
#     como Pregoeiro(a) ... sendo auxiliado(a) pelo(a) servidor(a) NOME2,
#     que atuará como equipe de apoio ..."
# O despacho da DFE só foi confirmado em 1 processo real até agora
# (23077.110448/2025-17) — reconferir contra mais processos reais conforme
# forem aparecendo antes de confiar cegamente no padrão em lote.
_PADROES_RESPONSAVEL_DFI = {
    "pesquisaPrecos": (
        ["NOTA INFORMATIVA.*PESQUISA DE PRE"],
        r"Respons[áa]vel pela pesquisa:\s*(.+?)\(Assinado",
    ),
    "irp": (
        ["NOTA INFORMATIVA.*INTEN[ÇC][ÃA]O DE REGISTRO"],
        r"Respons[áa]vel pela IRP:\s*(.+?)\(Assinado",
    ),
    "elaboracaoEdital": (
        ["NOTA INFORMATIVA.*ELABORA[ÇC][ÃA]O DE EDITAL"],
        r"Respons[áa]vel pela instru[çc][ãa]o:\s*(.+?)\(Assinado",
    ),
}


def extrair_responsaveis_dfi(client: SipacClient, docs) -> dict:
    """Lê o texto das 3 Notas Informativas da Fase Interna já presentes em
    `docs` (quando existirem) e extrai o nome do responsável indicado em
    cada uma. Só busca o texto quando o documento correspondente já existe
    na listagem — processos que ainda não chegaram naquela etapa
    simplesmente não geram nenhuma chamada extra ao SIPAC."""
    resultado: dict[str, str] = {}
    for chave, (tipo_padroes, regex_nome) in _PADROES_RESPONSAVEL_DFI.items():
        doc = next((d for d in docs if _match_any(d.tipo, tipo_padroes) and d.id_doc), None)
        if not doc:
            continue
        html_doc = client.obter_documento_texto(doc.id_doc)
        if html_doc is None:
            continue
        texto = texto_visivel(html_doc)
        m = _re.search(regex_nome, texto, _re.IGNORECASE)
        if m:
            resultado[chave] = m.group(1).strip().rstrip(".").strip()
    return resultado


_REGEX_PREGOEIRO = r"agente de contrata[çc][ãa]o\s+(.+?),\s*que atuar[áa] como Pregoeiro"
_REGEX_EQUIPE_APOIO = r"servidor\(a\)\s+(.+?),\s*que atuar[áa] como equipe de apoio"


def extrair_responsavel_dfe(client: SipacClient, docs) -> dict:
    """Procura, entre os despachos emitidos pela DFE, o primeiro cujo texto
    designa o pregoeiro (frase "que atuará como Pregoeiro") e extrai
    pregoeiro + equipe de apoio. O tipo de documento é só "DESPACHO"
    (genérico, usado pra várias coisas) — por isso confere o texto de cada
    um até achar o que bate, em vez de confiar só no tipo."""
    candidatos = [d for d in docs if "DFE" in d.origem.upper() and "DESPACHO" in d.tipo.upper() and d.id_doc]
    for doc in candidatos:
        html_doc = client.obter_documento_texto(doc.id_doc)
        if html_doc is None:
            continue
        texto = texto_visivel(html_doc)
        m_preg = _re.search(_REGEX_PREGOEIRO, texto, _re.IGNORECASE)
        if not m_preg:
            continue
        resultado = {"pregoeiro": m_preg.group(1).strip()}
        m_equipe = _re.search(_REGEX_EQUIPE_APOIO, texto, _re.IGNORECASE)
        if m_equipe:
            resultado["equipeApoio"] = m_equipe.group(1).strip()
        return resultado
    return {}


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
    "planejamento": "Planejamento (DPGC)",
    "faseInterna": "Fase Interna (DFI)",
    "faseExterna": "Fase Externa (DFE)",
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
    "planejamento": "planejamentoFim",
    "faseInterna": "faseInternaFim",
    "faseExterna": "faseExternaFim",
}

import re as _re


def _match_any(tipo: str, padroes: list[str]) -> bool:
    return any(_re.search(p, tipo, _re.IGNORECASE) for p in padroes)


def calcular_progresso(
    docs, etapas: list[tuple[str, list[str]]]
) -> tuple[str | None, dict, bool, list[tuple[str, list[str]]]]:
    """Varre os documentos em ordem e descobre até onde o processo avançou
    dentro de uma lista de etapas (sempre de UM processo-fonte só — nunca
    misturar planejamento com pregão, ver comentário acima).

    Retorna (subEtapa_atual, marcos, chegou_ao_fim_dessas_etapas, retrabalho).
    "retrabalho" lista as etapas cujo documento-gatilho apareceu mais de uma
    vez — sinal de que o processo pode ter saído do fluxo padrão (devolvido
    pra correção, reiniciado etc.) em algum momento. Não usamos isso pra
    mudar a sub-etapa automaticamente (mesmo raciocínio da trava de
    retrocesso: não dá pra distinguir com segurança "saiu do fluxo de
    verdade" de "documento reemitido/corrigido sem mudar de etapa") — só
    para sinalizar em avisos, pra confirmação manual."""
    marcos = {}
    ultima_completada_idx = -1
    retrabalho: list[tuple[str, list[str]]] = []
    for i, (chave, padroes) in enumerate(etapas):
        encontrados = [d for d in docs if _match_any(d.tipo, padroes)]
        if encontrados:
            marcos[MARCO_FIM_POR_SUBETAPA[chave]] = encontrados[0].data
            ultima_completada_idx = i
            if len(encontrados) > 1:
                retrabalho.append((chave, [d.data for d in encontrados]))

    chegou_ao_fim = ultima_completada_idx == len(etapas) - 1
    if chegou_ao_fim:
        return None, marcos, True, retrabalho

    proxima_idx = ultima_completada_idx + 1
    sub_atual = etapas[proxima_idx][0] if proxima_idx < len(etapas) else None
    return sub_atual, marcos, False, retrabalho


def detectar_estados_especiais(docs, movimentacoes, caminho: str = "pregao") -> dict:
    """Estados especiais do CLAUDE.md seção 8 — só pro caminho Pregão
    (recurso/suspensão são conceitos de licitação em disputa; Dispensa usa
    calcular_progresso_dispensa_execucao para seu próprio "concluido")."""
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
        "concluido": homologado,
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


def avisos_retrabalho(numero_processo: str, retrabalho: list[tuple[str, list[str]]]) -> list[str]:
    """Formata os avisos de possível saída do fluxo padrão (documento de uma
    etapa já concluída reaparecendo mais tarde) pra lista de avisos."""
    return [
        f"{numero_processo}: documento da etapa '{chave}' apareceu {len(datas)} vezes ({', '.join(datas)}) "
        f"— pode ter saído do fluxo padrão (devolvido pra correção, reiniciado etc.). Sub-etapa NÃO "
        f"alterada por isso; conferir manualmente se quiser."
        for chave, datas in retrabalho
    ]


def atualizar_todos() -> dict:
    data = json.loads(PROCESSOS_PATH.read_text(encoding="utf-8"))
    client = SipacClient()

    atualizados = 0
    avisos = []

    for p in data:
        caminho = p.get("caminho")
        # Adesão SRP e Concorrência sempre leem do processo_id direto — nunca
        # têm processo de execução separado a resolver (ver comentários
        # acima de cada um).
        SEMPRE_PROCESSO_ID = {
            "adesao_srp": SUBETAPAS_ADESAO_SRP,
            "concorrencia": SUBETAPAS_CONCORRENCIA,
            "concorrencia_compras": SUBETAPAS_CONCORRENCIA_COMPRAS,
        }
        caminhos_suportados = ("pregao", "dispensa", "inexigibilidade", *SEMPRE_PROCESSO_ID)
        if caminho not in caminhos_suportados or p.get("fase") == "Homologado":
            continue

        mudou = False
        subetapa_mudou = False
        concluido = False

        # Cada caminho usa nomes de campo próprios pro processo de execução
        # vinculado (pregão / dispensa / inexigibilidade), porque cada um
        # pode ter uma nomenclatura de tramitação diferente — CLAUDE.md
        # seção 4.
        campo_vinculo = "pregao" if caminho == "pregao" else "execucao_numero"
        campo_vinculo_id = "pregao_id" if caminho == "pregao" else "execucao_id"
        etapas_planejamento = {
            "pregao": SUBETAPAS_PLANEJAMENTO,
            "dispensa": SUBETAPAS_PLANEJAMENTO_DISPENSA,
            "inexigibilidade": SUBETAPAS_PLANEJAMENTO_INEXIGIBILIDADE,
        }.get(caminho)
        ordem = {
            "pregao": ORDEM_GLOBAL,
            "dispensa": ORDEM_DISPENSA,
            "inexigibilidade": ORDEM_INEXIGIBILIDADE,
            "adesao_srp": ORDEM_ADESAO_SRP,
            "concorrencia": ORDEM_CONCORRENCIA,
            "concorrencia_compras": ORDEM_CONCORRENCIA_COMPRAS,
        }[caminho]

        tem_execucao_vinculada = caminho not in SEMPRE_PROCESSO_ID and bool(p.get(campo_vinculo))

        if caminho in SEMPRE_PROCESSO_ID:
            if not p.get("processo_id"):
                avisos.append(f"{p['processo']}: sem processo_id resolvido — pulado.")
                continue
            html = client.obter_processo(p["processo_id"])
            docs = extrair_documentos(html)
            movs = extrair_movimentacoes(html)
            sub_atual, marcos_novos, concluido, retrabalho = calcular_progresso(docs, SEMPRE_PROCESSO_ID[caminho])
            avisos.extend(avisos_retrabalho(p["processo"], retrabalho))
            estados = {"concluido": concluido, "em_recurso": False, "candidato_suspensao": False}
        elif tem_execucao_vinculada:
            # Já formalizou o processo de execução: a etapa de Planejamento é
            # história do apenso e não é recalculada aqui — só a parte do
            # processo de execução é reavaliada (nunca misturar fonte,
            # CLAUDE.md seção 2).
            if not p.get(campo_vinculo_id):
                avisos.append(
                    f"{p['processo']}: tem {campo_vinculo}={p[campo_vinculo]!r} vinculado mas o id "
                    f"interno do SIPAC não está resolvido — pulado nesta execução."
                )
                continue
            html = client.obter_processo(p[campo_vinculo_id])
            docs = extrair_documentos(html)
            movs = extrair_movimentacoes(html)
            if caminho == "dispensa":
                sub_atual, marcos_novos, concluido, sem_disputa = calcular_progresso_dispensa_execucao(docs)
                if sem_disputa is not None and p.get("semDisputaFaseExterna") != sem_disputa:
                    p["semDisputaFaseExterna"] = sem_disputa
                    mudou = True
                estados = {"concluido": concluido, "em_recurso": False, "candidato_suspensao": False}
            elif caminho == "inexigibilidade":
                sub_atual, marcos_novos, concluido = calcular_progresso_inexigibilidade_execucao(docs)
                estados = {"concluido": concluido, "em_recurso": False, "candidato_suspensao": False}
            else:
                sub_atual, marcos_novos, _chegou_ao_fim, retrabalho = calcular_progresso(docs, SUBETAPAS_PREGAO)
                avisos.extend(avisos_retrabalho(p["processo"], retrabalho))
                estados = detectar_estados_especiais(docs, movs, caminho)

                # Responsáveis na DFI/DFE (seção acima) — só busca o texto
                # de um documento quando ainda falta o nome correspondente,
                # pra não reler o mesmo despacho/nota em toda execução.
                responsaveis_dfi_existentes = p.get("responsaveisDfi") or {}
                if len(responsaveis_dfi_existentes) < len(_PADROES_RESPONSAVEL_DFI):
                    novos_dfi = extrair_responsaveis_dfi(client, docs)
                    combinados = {**responsaveis_dfi_existentes, **novos_dfi}
                    if combinados != responsaveis_dfi_existentes:
                        p["responsaveisDfi"] = combinados
                        mudou = True

                responsaveis_dfe_existentes = p.get("responsaveisDfe") or {}
                if len(responsaveis_dfe_existentes) < 2:
                    novos_dfe = extrair_responsavel_dfe(client, docs)
                    combinados = {**responsaveis_dfe_existentes, **novos_dfe}
                    if combinados != responsaveis_dfe_existentes:
                        p["responsaveisDfe"] = combinados
                        mudou = True
        else:
            if not p.get("processo_id"):
                avisos.append(f"{p['processo']}: sem processo_id resolvido — pulado.")
                continue
            html = client.obter_processo(p["processo_id"])
            docs = extrair_documentos(html)
            movs = extrair_movimentacoes(html)
            sub_atual, marcos_novos, _chegou_ao_fim, retrabalho = calcular_progresso(docs, etapas_planejamento)
            avisos.extend(avisos_retrabalho(p["processo"], retrabalho))
            estados = {"concluido": False, "em_recurso": False, "candidato_suspensao": False}

        if estados["concluido"] and p.get("fase") != "Homologado":
            # "Homologado" é reaproveitado aqui como o balde genérico de
            # "processo de contratação concluído" (CLAUDE.md seção 7/8) —
            # pra Dispensa o gatilho real é a Nota de Empenho, não uma
            # Homologação de verdade, mas a semântica de painel é a mesma:
            # sai do acompanhamento ativo.
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
            idx_novo = ordem.index(sub_atual) if sub_atual in ordem else -1
            idx_atual = ordem.index(p["subEtapa"]) if p.get("subEtapa") in ordem else -1
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

        # Planejamento que já mudou de status (ex. "APENSADO") mas ainda não
        # tem o processo de execução vinculado no painel — não dá pra
        # descobrir automaticamente hoje (busca por número não funciona,
        # CLAUDE.md seção 12); sinaliza pra confirmação manual. A peça que
        # resolveria isso sozinha (varrer Termos de Juntada por tipo de
        # documento) ainda não foi construída — combinado com a pessoa dona
        # do projeto pra fazer depois do levantamento por caminho.
        if not tem_execucao_vinculada and caminho not in SEMPRE_PROCESSO_ID:
            status_mudou = "Status: APENSADO" in html or "Status: ARQUIVADO" in html
            enviado_a_dfi = any(
                "DFI" in mv.unidade_destino.upper() and "PLANEJAMENTO" not in mv.unidade_destino.upper()
                for mv in movs
            )
            if status_mudou or enviado_a_dfi:
                avisos.append(
                    f"{p['processo']}: sinais de que já saiu do planejamento (status/movimentação) "
                    f"mas ainda não tem processo de execução vinculado no painel — confirmar "
                    f"manualmente por enquanto."
                )

        if mudou:
            atualizados += 1
            # Checkpoint incremental — o levantamento histórico processa
            # centenas de processos numa única execução (cada um exige 1+
            # acesso ao SIPAC); salvar só no final arriscaria perder tudo se
            # o ambiente cair no meio, como já aconteceu algumas vezes nesta
            # sessão. Salvar a cada mudança é mais seguro que só no fim.
            PROCESSOS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    PROCESSOS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    caminhos_suportados = ("pregao", "dispensa", "inexigibilidade", "adesao_srp", "concorrencia", "concorrencia_compras")
    return {
        "processos_verificados": sum(1 for p in data if p.get("caminho") in caminhos_suportados),
        "atualizados": atualizados,
        "avisos": avisos,
    }


if __name__ == "__main__":
    resumo = atualizar_todos()
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
