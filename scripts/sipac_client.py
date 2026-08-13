"""
Cliente para a área pública do SIPAC/UFRN.

Reúne as técnicas de acesso já validadas empiricamente (ver CLAUDE.md, seção 12):
- Busca pública por Tipo de Processo funciona bem via POST automatizado.
- Busca pública por número de processo NÃO funciona via automação simples — não usar.
- Paginação de resultados via POST não é confiável — contornar com janelas de data estreitas.
- Links de documento são `href="#"` com a URL real dentro do atributo `onclick`.
- A conexão com o SIPAC é instável — toda chamada precisa de retry.
"""

from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from html import unescape

import requests

BASE = "https://sipac.ufrn.br"
PORTAL_URL = f"{BASE}/public/jsp/portal.jsf"
PROCESSO_DETALHADO_URL = f"{BASE}/public/jsp/processos/processo_detalhado.jsf"
DOC_VISUALIZACAO_URL = f"{BASE}/public/jsp/processos/documento_visualizacao.jsf"

# Tipos de processo confirmados (ver CLAUDE.md seção 4). Reconfirmar se a
# busca voltar zero resultados de forma persistente — o SIPAC já teve pelo
# menos um caso de value reciclado para outro tipo em anos diferentes.
TIPO_PROCESSO = {
    "planejamento": 314,       # PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO (33.00)
    "dispensa": 150,           # DISPENSA DE LICITAÇÃO
    "inexigibilidade": 74,     # INEXIGIBILIDADE DE LICITAÇÃO
    "adesao_srp": 258,         # ADESÃO SRP
    "concorrencia": 220,       # CONCORRÊNCIA
    "solicitacao_material_srp": 632,  # SOLICITAÇÃO DE MATERIAL EM REGISTRO DE PREÇO
}

DEFAULT_TIMEOUT = 20
DEFAULT_RETRIES = 4
DEFAULT_BACKOFF = 2.0


class SipacError(RuntimeError):
    pass


def _retry(fn, *, retries=DEFAULT_RETRIES, backoff=DEFAULT_BACKOFF, what=""):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except (requests.RequestException, ConnectionError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff * attempt)
    raise SipacError(f"Falha ao acessar SIPAC ({what}) após {retries} tentativas: {last_exc}")


class SipacClient:
    """Sessão com cookie jar persistente, como exige o fluxo de busca+paginação."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; PainelComprasUFRN/1.0)",
            }
        )

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return _retry(lambda: self._checked(self.session.get(url, **kwargs)), what=f"GET {url}")

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        return _retry(lambda: self._checked(self.session.post(url, **kwargs)), what=f"POST {url}")

    @staticmethod
    def _checked(resp: requests.Response) -> requests.Response:
        resp.raise_for_status()
        return resp

    # ------------------------------------------------------------------
    # Busca por Tipo de Processo (o único caminho de busca que funciona)
    # ------------------------------------------------------------------

    def _extrair_campo_select_tipo_processo(self, portal_html: str) -> str:
        """O `name` do <select> de Tipo de Processo muda a cada carregamento da
        página — precisa ser reextraído sempre, nunca hardcoded entre execuções."""
        m = re.search(
            r'name="(processoForm:j_id[^"]+)"[^>]*onclick="divPadraoP\(\'proc_p\', false\)"',
            portal_html,
        )
        if not m:
            # variação de ordem de atributos entre versões da página
            m = re.search(r'name="(processoForm:j_id[^"]+)"\s+size="1"', portal_html)
        if not m:
            raise SipacError("Não encontrei o campo de Tipo de Processo na página do portal — o SIPAC pode ter mudado o HTML.")
        return m.group(1)

    def _extrair_botao_consultar(self, portal_html: str) -> str:
        m = re.search(r'name="(processoForm:j_id[^"]+)" value="Consultar Processo"', portal_html)
        if not m:
            raise SipacError("Não encontrei o botão 'Consultar Processo' na página do portal.")
        return m.group(1)

    def buscar_processos_por_tipo(
        self, tipo_value: int, data_inicial: date, data_final: date
    ) -> list["ResultadoProcesso"]:
        """Busca processos por Tipo de Processo + Período de Cadastro.

        A janela de datas deve ser estreita o bastante para não truncar (o
        SIPAC não pagina de forma confiável via automação — ver CLAUDE.md
        seção 12). Uma janela de até ~15 dias costuma bastar para tipos de
        baixo volume; para tipos de alto volume (ex. Planejamento), usar
        janelas menores (semanais).
        """
        portal_resp = self.get(PORTAL_URL)
        campo_tipo = self._extrair_campo_select_tipo_processo(portal_resp.text)
        botao = self._extrair_botao_consultar(portal_resp.text)

        payload = {
            "processoForm": "processoForm",
            "aba": "p-processos",
            "tipo_consulta_processo": "500",
            campo_tipo: str(tipo_value),
            "tipo_consulta_cadastro": "400",
            # O campo é <input type="date">; o POST espera o formato ISO
            # (yyyy-mm-dd), não o formato brasileiro exibido na tela —
            # confirmado empiricamente (dd/mm/yyyy causa erro 500 no servidor).
            "DATA_INICIAL": data_inicial.isoformat(),
            "DATA_FINAL": data_final.isoformat(),
            botao: "Consultar Processo",
            "javax.faces.ViewState": "j_id1",
        }
        resp = self.post(PORTAL_URL, data=payload)
        return parse_resultados_busca(resp.text)

    # ------------------------------------------------------------------
    # Leitura de processo e documentos
    # ------------------------------------------------------------------

    def obter_processo(self, processo_id: int) -> str:
        resp = self.get(PROCESSO_DETALHADO_URL, params={"id": processo_id})
        return resp.text

    def obter_documento_texto(self, id_doc: int) -> str | None:
        """Tenta ler um documento como HTML direto (mais rápido). Retorna None
        se esse documento não tiver visualização HTML (ex.: é um PDF puro —
        nesse caso, usar obter_documento_pdf_url + baixar separadamente)."""
        resp = self.get(DOC_VISUALIZACAO_URL, params={"idDoc": id_doc})
        if resp.status_code == 200 and "<html" in resp.text.lower():
            return resp.text
        return None


@dataclass
class ResultadoProcesso:
    numero: str
    processo_id: int | None
    assunto: str
    situacao: str | None = None


@dataclass
class DocumentoProcesso:
    tipo: str
    data: str
    origem: str = ""
    id_doc: int | None = None


@dataclass
class Movimentacao:
    data_origem: str
    unidade_origem: str
    unidade_destino: str
    urgente: bool = False


def _normalizar(txt: str) -> str:
    txt = unescape(txt)
    # NFC (não NFKD): mantém acentos como caractere único composto (ex. "Ç"),
    # que é como aparecem no código-fonte deste projeto e nos padrões de
    # regex — NFKD decompõe em base+diacrítico e quebra silenciosamente
    # qualquer comparação literal com texto acentuado (bug real já visto:
    # todo processo caía na primeira sub-etapa porque nenhum padrão com
    # acento batia mais).
    txt = unicodedata.normalize("NFC", txt)
    return " ".join(txt.split())


_LINHA_RESULTADO_RE = re.compile(r"<tr>(.*?)</tr>", re.DOTALL)
_TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)
_NUMERO_PROCESSO_RE = re.compile(r"\d{5}\.\d{6}/\d{4}-\d{2}")
_PROCESSO_ID_RE = re.compile(r"processo_detalhado\.jsf\?id=(\d+)")


def parse_resultados_busca(html: str) -> list[ResultadoProcesso]:
    """Extrai a lista de processos da tabela de resultados da busca pública.

    Cada linha (<tr>) tem: nº do processo, assunto, unidade de origem
    (2x, resumida e detalhada), e um link 'Visualizar Processo' contendo
    `processo_detalhado.jsf?id=NNN`. Linhas sem esse link (cabeçalho,
    outras tabelas da mesma página) são ignoradas.
    """
    resultados: list[ResultadoProcesso] = []
    for row_m in _LINHA_RESULTADO_RE.finditer(html):
        row_html = row_m.group(1)
        id_m = _PROCESSO_ID_RE.search(row_html)
        if not id_m:
            continue
        cols = _TD_RE.findall(row_html)
        if len(cols) < 2:
            continue
        numero_m = _NUMERO_PROCESSO_RE.search(_normalizar(re.sub(r"<[^>]+>", " ", cols[0])))
        if not numero_m:
            continue
        assunto = _normalizar(re.sub(r"<[^>]+>", " ", cols[1])) if len(cols) > 1 else ""
        resultados.append(
            ResultadoProcesso(
                numero=numero_m.group(0), processo_id=int(id_m.group(1)), assunto=assunto
            )
        )
    return resultados


def extrair_num_registros_encontrados(html: str) -> int | None:
    m = re.search(r'(\d+)\s+Registro\(?s?\)?\s+Encontrado', html, re.IGNORECASE)
    return int(m.group(1)) if m else None


_TABELA_RE = re.compile(
    r'<table[^>]*class="subListagem"[^>]*>\s*<caption>([^<]*)</caption>(.*?)</table>',
    re.DOTALL,
)
_LINHA_RE = re.compile(r'<tr class="linha(?:Par|Impar)">(.*?)</tr>', re.DOTALL)
_IDDOC_RE = re.compile(r"documento_visualizacao\.jsf\?idDoc=(\d+)")


def _isolar_tabela(html: str, legenda: str) -> str | None:
    """Isola o HTML de uma <table class="subListagem"> pela legenda (<caption>),
    já que a página tem várias tabelas com a mesma classe CSS (Documentos,
    Movimentações, etc.) — não dá para diferenciar só pela classe."""
    alvo = _normalizar(legenda).lower()
    for m in _TABELA_RE.finditer(html):
        legenda_encontrada = _normalizar(unescape(m.group(1))).lower()
        if alvo in legenda_encontrada:
            return m.group(2)
    return None


def extrair_documentos(html: str) -> list[DocumentoProcesso]:
    """Extrai a tabela "Documentos do Processo": Ordem, Tipo do Documento,
    Data do Documento, Origem, Natureza, + link de visualização (idDoc)."""
    tabela_html = _isolar_tabela(html, "Documentos do Processo")
    if tabela_html is None:
        return []
    docs: list[DocumentoProcesso] = []
    for row_m in _LINHA_RE.finditer(tabela_html):
        row_html = row_m.group(1)
        cols = _TD_RE.findall(row_html)
        if len(cols) < 3:
            continue
        tipo = _normalizar(re.sub(r"<[^>]+>", " ", cols[1]))
        data_doc = _normalizar(re.sub(r"<[^>]+>", " ", cols[2]))
        origem = _normalizar(re.sub(r"<[^>]+>", " ", cols[3])) if len(cols) > 3 else ""
        id_m = _IDDOC_RE.search(row_html)
        if not tipo:
            continue
        docs.append(
            DocumentoProcesso(
                tipo=tipo,
                data=data_doc,
                origem=origem,
                id_doc=int(id_m.group(1)) if id_m else None,
            )
        )
    return docs


def extrair_movimentacoes(html: str) -> list[Movimentacao]:
    """Extrai a tabela "Movimentações do Processo": Data Origem, Unidade
    Origem, Unidade Destino, Urgente."""
    tabela_html = _isolar_tabela(html, "Movimentações do Processo")
    if tabela_html is None:
        return []
    movs: list[Movimentacao] = []
    for row_m in _LINHA_RE.finditer(tabela_html):
        row_html = row_m.group(1)
        cols = _TD_RE.findall(row_html)
        if len(cols) < 3:
            continue
        data_origem = _normalizar(re.sub(r"<[^>]+>", " ", cols[0]))
        unidade_origem = _normalizar(re.sub(r"<[^>]+>", " ", cols[1]))
        unidade_destino = _normalizar(re.sub(r"<[^>]+>", " ", cols[2]))
        urgente_txt = _normalizar(re.sub(r"<[^>]+>", " ", cols[-1])) if cols else ""
        if not data_origem:
            continue
        movs.append(
            Movimentacao(
                data_origem=data_origem,
                unidade_origem=unidade_origem,
                unidade_destino=unidade_destino,
                urgente="sim" in urgente_txt.lower(),
            )
        )
    return movs


def extrair_texto_termo_apensacao(html_doc: str) -> str | None:
    """Do HTML de um TERMO DE JUNTADA POR APENSAÇÃO, extrai o(s) número(s) de
    processo citados (ex.: 'apensar ao presente processo nº X o(s)
    processo(s) nº(s) Y')."""
    texto = _normalizar(re.sub(r"<[^>]+>", " ", html_doc))
    return texto
