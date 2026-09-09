"""
Gerador de Certificação Processual — pipeline completo.

Dado um número de processo (e, opcionalmente, o tipo/modalidade), busca o
processo no SIPAC público, extrai os campos necessários e gera o PDF da
Certificação Processual (art. 14, Portaria PGF nº 931/2018), seguindo o
modelo documentado em MODELO_CERTIFICACAO_PROCESSUAL.md.

Uso:
    python3 gerar_certificacao.py "23077.121155/2026-38" --tipo pregao
    python3 gerar_certificacao.py "23077.121155/2026-38" --tipo pregao --nome "João Paulo Paiva da Silva" --cargo "Diretor de Compras da UFRN"

Saída: um JSON no stdout com:
    {
      "status": "ok" | "erro",
      "erro": None | "mensagem",
      "avisos": [ ... ],          # campos que precisam de conferência manual
      "campos": { ... },          # tudo que foi extraído, pra auditoria
      "pdf_base64": "..."         # só quando status == "ok"
    }

Este script não decide sozinho o nome/cargo de quem assina — se não vierem
por parâmetro, ficam como placeholder no PDF (igual ao modelo manual).
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
from datetime import date

sys.path.insert(0, __file__.rsplit("/", 1)[0])

import fitz  # noqa: E402

from sipac_client import (  # noqa: E402
    SipacClient,
    SipacError,
    TIPO_PROCESSO,
    extrair_assunto_detalhado,
    extrair_documentos,
    extrair_interessados,
    extrair_texto_termo_apensacao,
    texto_visivel,
)

AGU_URL = (
    "https://www.gov.br/agu/pt-br/composicao/consultoria-geral-da-uniao-1/"
    "modelos-de-convenios-licitacoes-e-contratos/modelos-de-licitacoes-e-contratos"
)

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


# ----------------------------------------------------------------------
# 1. Localizar o processo
# ----------------------------------------------------------------------

def localizar_processo(client: SipacClient, numero: str, tipo: str) -> dict:
    tipo_value = TIPO_PROCESSO.get(tipo)
    if tipo_value is None:
        raise SipacError(f"Tipo de processo desconhecido: {tipo!r}. Opções: {list(TIPO_PROCESSO)}")
    resultado = client.buscar_por_numero_paginado(tipo_value, numero, max_paginas=40)
    if resultado is None:
        raise SipacError(
            f"Não encontrei o processo {numero!r} buscando por Tipo de Processo = {tipo!r} "
            "nas primeiras ~600 ocorrências (mais recentes primeiro). Confirme o número e a "
            "modalidade, ou o processo pode ser antigo demais pra essa busca."
        )
    return {"numero": resultado.numero, "id": resultado.processo_id, "assunto_curto": resultado.assunto}


# ----------------------------------------------------------------------
# 2. Apensado
# ----------------------------------------------------------------------

_APENSADO_NUM_RE = re.compile(r"processo\(s\)\s*n[ºo]\(s\)\s*(\d{5}\.\d{6}/\d{4}-\d{2})", re.IGNORECASE)


def resolver_apensado(client: SipacClient, docs: list, avisos: list) -> dict | None:
    doc_apensacao = next((d for d in docs if "JUNTADA POR APENSA" in d.tipo.upper()), None)
    if doc_apensacao is None:
        return None
    if doc_apensacao.id_doc is None:
        avisos.append("Encontrei um Termo de Juntada por Apensação, mas não consegui abri-lo (sem idDoc).")
        return None
    html_doc = client.obter_documento_texto(doc_apensacao.id_doc)
    if not html_doc:
        avisos.append("Encontrei um Termo de Juntada por Apensação, mas não consegui ler o conteúdo.")
        return None
    texto = extrair_texto_termo_apensacao(html_doc)
    m = _APENSADO_NUM_RE.search(texto or "")
    if not m:
        avisos.append("Encontrei um Termo de Juntada por Apensação, mas não consegui extrair o número do processo apensado — conferir manualmente.")
        return None
    numero_apensado = m.group(1)

    # Tenta descobrir a natureza do apensado — geralmente é Planejamento (314).
    descricao = None
    try:
        r = client.buscar_por_numero_paginado(TIPO_PROCESSO["planejamento"], numero_apensado, max_paginas=15)
        if r and r.processo_id:
            html_apensado = client.obter_processo(r.processo_id)
            assunto_apensado = extrair_assunto_detalhado(html_apensado)
            if assunto_apensado:
                descricao = "Processo de planejamento."
    except SipacError:
        pass
    if descricao is None:
        avisos.append(
            f"Não confirmei a natureza do processo apensado {numero_apensado} (tentei achá-lo como "
            "Planejamento e não achei) — no PDF ficou só \"Processo apensado.\", conferir manualmente."
        )
        descricao = "Processo apensado."
    return {"numero": numero_apensado, "descricao": descricao}


# ----------------------------------------------------------------------
# 3. Solicitação (Requisição de Materiais/Serviços)
# ----------------------------------------------------------------------

_REQUISICAO_RE = re.compile(r"REQUISIÇÃO DE (?:MATERIAIS|SERVIÇOS)\s*-\s*Nº\s*([\d\/]+)", re.IGNORECASE)


def resolver_solicitacao(client: SipacClient, docs: list, avisos: list) -> dict | None:
    doc_relatorio = next(
        (d for d in docs if "RELATÓRIO DETALHADO DE REQUISIÇÕES DO PROCESSO" in d.tipo.upper()), None
    )
    if doc_relatorio is None:
        avisos.append("Não encontrei nenhum \"Relatório Detalhado de Requisições do Processo\" — campo Solicitação nº ficou em branco.")
        return None
    ordem = docs.index(doc_relatorio) + 1
    texto = None
    if doc_relatorio.id_doc:
        html_doc = client.obter_documento_texto(doc_relatorio.id_doc)
        if html_doc:
            texto = texto_visivel(html_doc)
    if texto is None and doc_relatorio.id_arquivo and doc_relatorio.arquivo_key:
        pdf_bytes = client.obter_documento_pdf_bytes(doc_relatorio.id_arquivo, doc_relatorio.arquivo_key)
        if pdf_bytes:
            texto = _extrair_texto_pdf(pdf_bytes)
    if not texto:
        avisos.append("Encontrei o Relatório Detalhado de Requisições, mas não consegui ler o conteúdo — campo Solicitação nº ficou em branco.")
        return None
    achados = _REQUISICAO_RE.findall(texto)
    if not achados:
        avisos.append("Abri o Relatório Detalhado de Requisições, mas não achei nenhuma \"REQUISIÇÃO DE MATERIAIS/SERVIÇOS - Nº ...\" dentro — campo Solicitação nº ficou em branco.")
        return None
    primeira = achados[0]
    rotulo = f"REQUISIÇÃO DE MATERIAIS - Nº {primeira}" if len(achados) == 1 else f"REQUISIÇÃO DE MATERIAIS - Nº {primeira} e demais"
    return {"rotulo": rotulo, "documento_ordem": ordem}


# ----------------------------------------------------------------------
# 4. Relatório de Alterações — Minutas da AGU
# ----------------------------------------------------------------------

def resolver_relatorio_alteracoes(docs: list, avisos: list) -> int | None:
    doc = next((d for d in docs if "RELATÓRIO DE ALTERAÇÕES" in d.tipo.upper() and "AGU" in d.tipo.upper()), None)
    if doc is None:
        avisos.append(
            "Não encontrei um \"Relatório de Alterações - Minutas da AGU\" neste processo — a declaração "
            "final (página 2) ficou genérica, sem citar documento de referência. Revisar manualmente se "
            "esse processo usa a versão detalhada da declaração (checkboxes de inclusão/supressão/cláusula) "
            "em vez da versão resumida."
        )
        return None
    return docs.index(doc) + 1


# ----------------------------------------------------------------------
# 5. TR/Edital — objeto, valor, critério, versão do modelo AGU
# ----------------------------------------------------------------------

def _extrair_texto_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(doc[i].get_text() for i in range(len(doc)))


def resolver_dados_edital(client: SipacClient, docs: list, avisos: list) -> dict:
    dados = {
        "objeto": None, "valor": None, "criterio_julgamento": None,
        "srp": None, "versao_modelo_agu": None,
    }
    doc_tr = None
    for d in docs:
        if d.tipo.upper() == "TERMO DE REFERÊNCIA":
            doc_tr = d  # fica com a última ocorrência (mais recente na lista)
    doc_edital = None
    for d in docs:
        if "MINUTA DE EDITAL PARA LICITAÇÃO" in d.tipo.upper():
            doc_edital = d

    texto_tr = _baixar_texto_doc(client, doc_tr) if doc_tr else None
    texto_edital = _baixar_texto_doc(client, doc_edital) if doc_edital else None

    if texto_edital:
        m = re.search(r"OBJETO\s*\n(.+?)\n\s*VALOR\s*TOTAL", texto_edital, re.IGNORECASE | re.DOTALL)
        if m:
            dados["objeto"] = " ".join(m.group(1).split())
        m = re.search(r"VALOR\s*TOTAL\s*DA\s*CONTRATAÇÃO\s*\n(.+?)(?:\n\s*DATA|\n\s*CRITÉRIO)", texto_edital, re.IGNORECASE | re.DOTALL)
        if m:
            dados["valor"] = " ".join(m.group(1).split())
        m = re.search(r"CRITÉRIO\s*DE\s*JULGAMENTO:?\s*\n(.+)", texto_edital, re.IGNORECASE)
        if m:
            dados["criterio_julgamento"] = m.group(1).strip().splitlines()[0].strip()
        dados["srp"] = bool(re.search(r"REGISTRO\s+DE\s+PRE[ÇC]OS", texto_edital, re.IGNORECASE))

    _VERSAO_RE = re.compile(
        r"(Termo de Referência|Edital)\s*-\s*(.+?)\s*-\s*Atualização:\s*(\w+/\d{4})",
        re.IGNORECASE,
    )
    m_tr = _VERSAO_RE.search(texto_tr) if texto_tr else None
    m_edital = _VERSAO_RE.search(texto_edital) if texto_edital else None
    if m_tr:
        dados["versao_modelo_agu"] = f"{m_tr.group(2).strip()} - Atualização: {m_tr.group(3).strip()}"
    elif m_edital:
        dados["versao_modelo_agu"] = f"{m_edital.group(2).strip()} - Atualização: {m_edital.group(3).strip()}"

    # Comparação independente do rótulo — o rodapé do Edital raramente traz o
    # prefixo "Edital -"/"Termo de Referência -" que _VERSAO_RE exige, então a
    # checagem de divergência usa uma captura mais solta, só da data.
    _DATA_ATUALIZACAO_RE = re.compile(r"Atualiza[çc][ãa]o:\s*(\w+/\d{4})", re.IGNORECASE)
    m_data_tr = _DATA_ATUALIZACAO_RE.search(texto_tr) if texto_tr else None
    m_data_edital = _DATA_ATUALIZACAO_RE.search(texto_edital) if texto_edital else None
    if m_data_tr and m_data_edital and m_data_tr.group(1).strip().lower() != m_data_edital.group(1).strip().lower():
        avisos.append(
            f"O rodapé do Termo de Referência indica atualização \"{m_data_tr.group(1).strip()}\" e o do "
            f"Edital indica \"{m_data_edital.group(1).strip()}\" — datas diferentes. Usei a do TR no campo "
            "\"versão do modelo AGU\", mas conferir manualmente qual está correta."
        )

    if dados["objeto"] is None:
        avisos.append("Não consegui extrair automaticamente a Descrição do Objeto do Edital/TR — conferir e preencher manualmente.")
    if dados["valor"] is None:
        avisos.append("Não consegui extrair automaticamente o Valor Estimado do Edital — conferir e preencher manualmente.")
    if dados["criterio_julgamento"] is None:
        avisos.append("Não consegui extrair automaticamente o Critério de Julgamento (menor preço por item/grupo etc.) — conferir manualmente.")
    if dados["versao_modelo_agu"] is None:
        avisos.append("Não consegui extrair automaticamente a versão do modelo AGU usada (rodapé do TR) — campo ficou genérico, conferir manualmente.")

    return dados


def _baixar_texto_doc(client: SipacClient, doc) -> str | None:
    if doc is None:
        return None
    if doc.id_arquivo and doc.arquivo_key:
        pdf_bytes = client.obter_documento_pdf_bytes(doc.id_arquivo, doc.arquivo_key)
        if pdf_bytes:
            try:
                return _extrair_texto_pdf(pdf_bytes)
            except Exception:
                return None
    if doc.id_doc:
        html_doc = client.obter_documento_texto(doc.id_doc)
        if html_doc:
            return texto_visivel(html_doc)
    return None


# ----------------------------------------------------------------------
# 6. Montagem do PDF (layout — ver MODELO_CERTIFICACAO_PROCESSUAL.md)
# ----------------------------------------------------------------------

W, H = fitz.paper_size("a4")
MARGIN = 56
PAD = 10
FONT, FONT_B, FONT_I = "helv", "hebo", "heit"
GRAY = (0.90, 0.90, 0.90)
HEADER_LINES = [
    "ADVOCACIA-GERAL DA UNIÃO",
    "PROCURADORIA-GERAL FEDERAL",
    "DEPARTAMENTO DE CONSULTORIA - DEPCONSU",
    "EQUIPE DE TRABALHO REMOTO DE LICITAÇÕES E CONTRATOS - ETRLIC",
]


def _centered(page, y, text, size=9, font=FONT_B):
    tl = fitz.get_text_length(text, fontname=font, fontsize=size)
    page.insert_text(fitz.Point((W - tl) / 2, y), text, fontsize=size, fontname=font)


def _cap_baseline(y_top, bar_h, size):
    return y_top + bar_h / 2 + 0.36 * size


class _Writer:
    def __init__(self, page, y, left=MARGIN):
        self.page, self.y, self.left = page, y, left

    def line(self, text="", size=10, bold=False, italic=False, gap=15, indent=0):
        font = FONT_B if bold else (FONT_I if italic else FONT)
        if text:
            self.page.insert_text(fitz.Point(self.left + indent, self.y), text, fontsize=size, fontname=font)
        self.y += gap

    def wrap(self, text, size=10, bold=False, gap=13.5, indent=0, extra_gap_after=6, right=None):
        font = FONT_B if bold else FONT
        right_margin = right if right else (W - MARGIN)
        rect = fitz.Rect(self.left + indent, self.y - 9, right_margin, self.y + 400)
        self.page.insert_textbox(rect, text, fontsize=size, fontname=font, align=0, lineheight=1.25)
        avail_width = right_margin - (self.left + indent)
        chars_per_line = max(10, int(avail_width / (size * 0.5)))
        n_lines = max(1, math.ceil(len(text) / chars_per_line))
        self.y += n_lines * (size * 1.25) + extra_gap_after

    def space(self, h=10):
        self.y += h


def _new_page(doc):
    page = doc.new_page(width=W, height=H)
    y = 50
    for line in HEADER_LINES:
        _centered(page, y, line, size=9, font=FONT_B)
        y += 12
    page.draw_line(fitz.Point(MARGIN, y + 4), fitz.Point(W - MARGIN, y + 4), width=0.7)
    return page, y + 22


def _box_header(page, y_top, title, subtitle=None, bar_h=34):
    page.draw_rect(fitz.Rect(MARGIN, y_top, W - MARGIN, y_top + bar_h), color=(0, 0, 0), fill=GRAY, width=0.7)
    title_size = 12
    ty = y_top + 15 if subtitle else _cap_baseline(y_top, bar_h, title_size)
    _centered(page, ty, title, size=title_size, font=FONT_B)
    if subtitle:
        _centered(page, ty + 14, subtitle, size=9, font=FONT_I)
    return y_top + bar_h


def _section_box_start(page, y_top, title, bar_h=22):
    page.draw_rect(fitz.Rect(MARGIN, y_top, W - MARGIN, y_top + bar_h), color=(0, 0, 0), fill=GRAY, width=0.7)
    size = 10.5
    _centered(page, _cap_baseline(y_top, bar_h, size), title, size=size, font=FONT_B)
    return y_top + bar_h


def _section_box_end(page, y_top, y_bottom):
    page.draw_rect(fitz.Rect(MARGIN, y_top, W - MARGIN, y_bottom), color=(0, 0, 0), fill=None, width=0.7)


def gerar_pdf(campos: dict) -> bytes:
    """`campos` — ver `montar_campos()` mais abaixo pro formato esperado."""
    doc = fitz.open()

    # --- Página 1 ---
    page, y = _new_page(doc)
    y = _box_header(page, y, "CERTIFICAÇÃO PROCESSUAL", "Art. 14 da Portaria PGF n º 931/2018") + 14

    box1_top = y
    content_top = _section_box_start(page, box1_top, "IDENTIFICAÇÃO PROCESSUAL")
    w = _Writer(page, content_top + 16, left=MARGIN + PAD)
    w.line(f"Processo n.  {campos['numero']}", size=10, bold=True, gap=17)
    w.line("Volume (s): Processo eletrônico", size=10, bold=True, gap=17)
    if campos["apensado"]:
        w.line("Há processo (s) apensado (s)? (   ) Não (X) Sim", size=10, bold=True, gap=15)
        w.line(f"Processo  {campos['apensado']['numero']}", size=10, italic=True, gap=14)
        w.line(campos["apensado"]["descricao"], size=10, gap=20)
    else:
        w.line("Há processo (s) apensado (s)? (X) Não (   ) Sim", size=10, bold=True, gap=20)
    w.line("Interessado (s):", size=10, bold=True, gap=14)
    w.wrap("; ".join(campos["interessados"]) or "(não identificado)", size=10, bold=True, gap=13,
           extra_gap_after=6, right=W - MARGIN - PAD)
    w.space(14)
    _section_box_end(page, box1_top, w.y)
    y = w.y + 22

    box2_top = y
    content_top = _section_box_start(page, box2_top, "CARACTERIZAÇÃO LICITATÓRIA")
    w = _Writer(page, content_top + 18, left=MARGIN + PAD)
    aquisicao = campos["aquisicao"]
    sol = campos["solicitacao"]
    sol_rotulo = sol["rotulo"] if sol else "_________________"
    sol_doc = f"( documento {sol['documento_ordem']} )" if sol else "( documento          )"
    w.line(f"({'X' if aquisicao else ' '}) Aquisição", size=10, gap=15)
    w.line(f"Solicitação nº: {sol_rotulo if aquisicao else '_________________'} {sol_doc if aquisicao else ''} (SEI            )",
           size=10, indent=14, gap=20)
    w.line(f"({'X' if not aquisicao else ' '}) Serviços", size=10, gap=15)
    w.line(f"Solicitação nº: {sol_rotulo if not aquisicao else '_________________'} {sol_doc if not aquisicao else ''} (SEI            )",
           size=10, indent=14, gap=22)
    w.line("MODALIDADE:", size=10, bold=True, italic=True, gap=17)
    modalidades = ["Adesão SRP", "Aditivo", "Concorrência", "Concurso", "Consulta"]
    marcada = campos["modalidade"]
    linha1 = "     ".join(f"({'X' if m == marcada else ' '}) {m}" for m in modalidades)
    w.line(linha1, size=10, gap=16)
    modalidades2 = ["Convite", "Leilão", "Pregão", "Pregão com SRP", "RDC"]
    linha2 = "     ".join(f"({'X' if m == marcada else ' '}) {m}" for m in modalidades2)
    w.line(linha2, size=10, gap=16)
    w.line(f"({'X' if marcada == 'Tomada de Preços' else ' '}) Tomada de Preços", size=10, gap=22)
    w.line("CONTRATAÇÃO DIRETA", size=10, bold=True, italic=True, gap=17)
    cd = campos.get("contratacao_direta")
    w.line(f"({'X' if cd == 'Dispensa' else ' '}) Dispensa     ({'X' if cd == 'Inexigibilidade' else ' '}) Inexigibilidade", size=10, gap=15)
    w.space(10)
    _section_box_end(page, box2_top, w.y)

    # --- Página 2 ---
    page, y = _new_page(doc)
    box3_top = y
    w = _Writer(page, box3_top + 22, left=MARGIN + PAD)
    tipo_julg = campos.get("criterio_julgamento") or ""
    por_item = "por item" in tipo_julg.lower() or not tipo_julg
    por_grupo = "por grupo" in tipo_julg.lower()
    w.line("TIPO:", size=10, bold=True, gap=18)
    w.line(f"(X) Menor Preço:  ({'X' if por_item else ' '}) por item    ({'X' if por_grupo else ' '}) por grupo    (   ) por item e grupo",
           size=10, gap=16)
    w.line("(   ) Melhor Técnica     (   ) Técnica e Preço", size=10, gap=20)
    objeto = campos.get("objeto") or "(não extraído automaticamente — preencher manualmente)"
    w.wrap(f"Descrição do objeto: {objeto}", size=10, gap=13.5, extra_gap_after=14, right=W - MARGIN - PAD)
    w.line("Valor Estimado da contratação/aquisição: (numérico e por extenso)", size=10, gap=15)
    valor = campos.get("valor") or "(não extraído automaticamente — preencher manualmente)"
    w.wrap(valor, size=10, gap=13.5, extra_gap_after=14, right=W - MARGIN - PAD)
    _section_box_end(page, box3_top, w.y)
    y = w.y + 26

    w = _Writer(page, y, left=MARGIN)
    w.line("CERTIFICO:", size=10, bold=True, gap=20)
    versao = campos.get("versao_modelo_agu") or "(versão não identificada automaticamente)"
    relatorio_alt = campos.get("relatorio_alteracoes_ordem")
    ref_relatorio = f"o Relatório de Alterações - Minutas da AGU (documento {relatorio_alt} do processo)" if relatorio_alt else "o Relatório de Alterações - Minutas da AGU (documento não identificado — conferir)"
    w.wrap(f"( X ) Que as minutas integrantes do presente processo foram extraídas do sítio eletrônico da "
           f"Advocacia-Geral da União - AGU (Modelos de Licitações e Contratos) no endereço {AGU_URL}; "
           f"tendo sido adotada a versão {versao}, atualizada de acordo com {ref_relatorio}.",
           size=10, gap=13.5, extra_gap_after=13)
    w.wrap("( X ) Que conferi tratar-se de modelos de minutas atualizados, nos termos do art. 14, da "
           "Portaria PGF nº 931/2018; e", size=10, gap=13.5, extra_gap_after=13)
    w.wrap("( X ) Que a instrução processual foi devidamente cotejada com as listas de verificação "
           "(checklists) disponíveis no mesmo sítio acima apontado, justificando nos autos os documentos "
           "faltantes (caso seja necessário).", size=10, gap=13.5, extra_gap_after=12)

    w.space(20)
    w.wrap(f"DECLARO que as inclusões (em verde), as exclusões (em vermelho) e as alterações (em azul) "
           f"estão devidamente indicadas, com as correspondentes justificativas em {ref_relatorio}.",
           size=10, gap=13.5, extra_gap_after=20)
    w.line("DECLARO, ao final, possuir competência para firmar a presente certificação.", size=10, gap=40)
    hoje = date.today()
    w.line(f"NATAL/RN, {hoje.day:02d} de {MESES[hoje.month - 1]} de {hoje.year}", size=10, gap=60)
    w.line("_________________________________", size=10, gap=15)
    w.line(campos.get("nome") or "________________________________", size=10, gap=13)
    w.line(campos.get("cargo") or "Diretoria de Compras da UFRN", size=10, gap=13)

    return doc.tobytes()


# ----------------------------------------------------------------------
# 7. Orquestração
# ----------------------------------------------------------------------

def gerar_certificacao(numero: str, tipo: str, nome: str | None = None, cargo: str | None = None) -> dict:
    avisos: list[str] = []
    client = SipacClient()
    try:
        processo = localizar_processo(client, numero, tipo)
        html = client.obter_processo(processo["id"])
        assunto_detalhado = extrair_assunto_detalhado(html) or processo["assunto_curto"]
        interessados = extrair_interessados(html)
        docs = extrair_documentos(html)

        aquisicao = "aquisiç" in assunto_detalhado.lower() or "aquisic" in assunto_detalhado.lower()
        apensado = resolver_apensado(client, docs, avisos)
        solicitacao = resolver_solicitacao(client, docs, avisos)
        relatorio_alt_ordem = resolver_relatorio_alteracoes(docs, avisos)
        dados_edital = resolver_dados_edital(client, docs, avisos)

        modalidade = "Pregão com SRP" if dados_edital.get("srp") else "Pregão"
        contratacao_direta = None
        if tipo == "dispensa":
            modalidade, contratacao_direta = None, "Dispensa"
        elif tipo == "inexigibilidade":
            modalidade, contratacao_direta = None, "Inexigibilidade"
        elif tipo == "concorrencia":
            modalidade = "Concorrência"
        elif tipo == "adesao_srp":
            modalidade = "Adesão SRP"

        if not interessados:
            avisos.append("Não consegui extrair a lista de Interessados — campo ficou vazio, preencher manualmente.")

        campos = {
            "numero": processo["numero"],
            "apensado": apensado,
            "interessados": interessados,
            "aquisicao": aquisicao,
            "solicitacao": solicitacao,
            "modalidade": modalidade,
            "contratacao_direta": contratacao_direta,
            "relatorio_alteracoes_ordem": relatorio_alt_ordem,
            "nome": nome,
            "cargo": cargo,
            **dados_edital,
        }
        pdf_bytes = gerar_pdf(campos)
        return {
            "status": "ok",
            "erro": None,
            "avisos": avisos,
            "campos": {k: v for k, v in campos.items() if k not in ()},
            "pdf_base64": base64.b64encode(pdf_bytes).decode("ascii"),
        }
    except SipacError as exc:
        return {"status": "erro", "erro": str(exc), "avisos": avisos, "campos": {}, "pdf_base64": None}


def main():
    parser = argparse.ArgumentParser(description="Gera a Certificação Processual de um processo do SIPAC/UFRN.")
    parser.add_argument("numero", help="Número do processo, ex.: 23077.121155/2026-38")
    parser.add_argument("--tipo", default="pregao", choices=sorted(TIPO_PROCESSO.keys()),
                         help="Modalidade/tipo de processo (default: pregao)")
    parser.add_argument("--nome", default=None, help="Nome de quem assina (opcional)")
    parser.add_argument("--cargo", default=None, help="Cargo de quem assina (opcional)")
    parser.add_argument("--saida", default=None, help="Se passado, também salva o PDF nesse caminho")
    args = parser.parse_args()

    resultado = gerar_certificacao(args.numero, args.tipo, args.nome, args.cargo)
    if args.saida and resultado["pdf_base64"]:
        with open(args.saida, "wb") as f:
            f.write(base64.b64decode(resultado["pdf_base64"]))
        resultado_para_print = {**resultado, "pdf_base64": f"<salvo em {args.saida}>"}
    else:
        resultado_para_print = resultado
    print(json.dumps(resultado_para_print, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
