#!/usr/bin/env python3
"""
Piloto: pra uma lista de processos do portão, busca a lista de documentos e
lê o conteúdo de até 5 (todos se <=5; senão primeiro + último + 3 aleatórios
do meio), tentando HTML direto e caindo pra PDF quando não tiver.

Não decide nada sozinho — só prepara o material (texto de cada documento
lido) pra leitura humana/Claude decidir o resumo e o destino sugerido.

Uso: python3 scripts/piloto_analise_portao.py <processo_id> [<processo_id> ...]
Saída: JSON no stdout.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sipac_client import SipacClient, extrair_documentos  # noqa: E402

MAX_DOCS = 5
MAX_CHARS_POR_DOC = 3000


def escolher_docs(docs: list) -> list:
    if len(docs) <= MAX_DOCS:
        return docs
    meio = docs[1:-1]
    random.seed(hash(tuple(d.tipo for d in docs)) & 0xFFFFFFFF)
    escolhidos_meio = random.sample(meio, min(3, len(meio)))
    return [docs[0], *escolhidos_meio, docs[-1]]


def ler_texto_doc(client: SipacClient, d) -> str | None:
    if d.id_doc:
        texto = client.obter_documento_texto(d.id_doc)
        if texto:
            from sipac_client import texto_visivel
            return texto_visivel(texto)[:MAX_CHARS_POR_DOC]
    if d.id_arquivo and d.arquivo_key:
        texto = client.obter_documento_pdf_texto(d.id_arquivo, d.arquivo_key)
        if texto:
            return texto[:MAX_CHARS_POR_DOC]
    return None


def processar(processo_id: int) -> dict:
    client = SipacClient()
    html = client.obter_processo(processo_id)
    docs = extrair_documentos(html)
    escolhidos = escolher_docs(docs)

    lidos = []
    for d in escolhidos:
        texto = ler_texto_doc(client, d)
        lidos.append({
            "tipo": d.tipo,
            "data": d.data,
            "origem": d.origem,
            "texto": texto,
            "lido": texto is not None,
        })

    return {
        "processo_id": processo_id,
        "total_documentos": len(docs),
        "documentos_lidos": lidos,
    }


if __name__ == "__main__":
    ids = [int(a) for a in sys.argv[1:]]
    resultado = [processar(pid) for pid in ids]
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
