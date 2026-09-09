# Modelo — Certificação Processual

Documento de certificação exigido pelo **art. 14 da Portaria PGF nº 931/2018**, presente nos
processos de licitação da UFRN antes do encaminhamento à Procuradoria Federal. Aprendido e
validado em 09/09/2026, a partir de dois documentos reais fornecidos pela pessoa: um modelo em
branco oficial da ETRLIC/AGU e um exemplo real já preenchido e assinado (processo
23077.169444/2024-56, manutenção de eletrodomésticos das Residências Universitárias).

Primeiro caso gerado do zero e validado: **processo 23077.121155/2026-38** (Pregão Eletrônico
SISRP nº 132/2026 — aquisição de gêneros alimentícios).

---

## 1. Estrutura do documento (3 páginas)

Cabeçalho repetido no topo de cada página (centralizado, negrito):
```
ADVOCACIA-GERAL DA UNIÃO
PROCURADORIA-GERAL FEDERAL
DEPARTAMENTO DE CONSULTORIA - DEPCONSU
EQUIPE DE TRABALHO REMOTO DE LICITAÇÕES E CONTRATOS - ETRLIC
```
seguido de uma linha horizontal.

### Página 1
- Faixa cinza com título **CERTIFICAÇÃO PROCESSUAL** (centralizado, negrito) + subtítulo em
  itálico "Art. 14 da Portaria PGF n º 931/2018".
- Quadro (borda + faixa cinza de título) **IDENTIFICAÇÃO PROCESSUAL**:
  - Processo n. [número]
  - Volume (s): Processo eletrônico
  - Há processo (s) apensado (s)? ( ) Não (X) Sim → Processo [número apensado] + "Processo de
    planejamento." (ou outra natureza, conforme o caso)
  - Interessado (s): [lista de unidades]
- Quadro **CARACTERIZAÇÃO LICITATÓRIA** (mesmo estilo de borda/faixa):
  - (X) Aquisição **ou** (X) Serviços, com "Solicitação nº: ... ( documento N ) (SEI )"
  - MODALIDADE (negrito itálico, sem faixa própria — dentro do mesmo quadro): Adesão SRP,
    Aditivo, Concorrência, Concurso, Consulta, Convite, Leilão, Pregão, Pregão com SRP, RDC,
    Tomada de Preços
  - CONTRATAÇÃO DIRETA (idem): Dispensa, Inexigibilidade

### Página 2
- Quadro (borda, sem faixa cinza de título) com **TIPO** (Menor Preço — por item/grupo/item e
  grupo —, Melhor Técnica, Técnica e Preço), **Descrição do objeto** e **Valor Estimado**
  (numérico e por extenso).
- Fora do quadro, **CERTIFICO:** com três afirmações fixas (adaptar apenas a versão do modelo AGU
  e a referência do Relatório de Alterações):
  1. Que as minutas foram extraídas do site da AGU (Modelos de Licitações e Contratos), adotada a
     versão **[nome exato da versão, ver seção 2]**, atualizada conforme o Relatório de Alterações
     - Minutas da AGU (documento N do processo).
  2. Que conferiu tratar-se de modelo atualizado (art. 14, Portaria PGF 931/2018).
  3. Que a instrução foi cotejada com os checklists do mesmo site, justificando documentos
     faltantes se houver.

### Página 3
- Sem quadro, texto corrido:
  - "DECLARO que as inclusões (em verde), as exclusões (em vermelho) e as alterações (em azul)
    estão devidamente indicadas, com as correspondentes justificativas no Relatório de Alterações
    - Minutas da AGU (documento N do processo)." — versão resumida, usada quando existe um
    documento "RELATÓRIO DE ALTERAÇÕES - MINUTAS DA AGU" no processo (é o caso mais comum
    observado até agora).
  - "DECLARO, ao final, possuir competência para firmar a presente certificação."
  - Local/data, assinatura (nome, cargo).

**Existe também uma versão detalhada** dessa declaração final, vista no modelo em branco oficial,
com checkboxes separados para "nenhuma alteração" / "inclusão de trecho" (Edital/Contrato/TR, com
motivo) / "supressão de trecho" (idem) / "cláusula específica incluída" (idem). Usar essa versão
apenas se não houver um Relatório de Alterações único cobrindo tudo, ou se a pessoa pedir
explicitamente a forma detalhada.

---

## 2. Onde puxar cada dado no processo (SIPAC)

Todos os dados devem vir do processo real — nunca presumir/inventar. Passo a passo:

1. **Achar o processo pelo número**: a busca direta por "N° Processo" no portal público não
   funciona (limitação já documentada na seção 12 do `CLAUDE.md`). Buscar por **Tipo de
   Processo** (ex.: `151` = Pregão) e paginar até achar — ver seção 4 deste documento para a
   técnica de paginação corrigida.
2. **Interessado(s)**: seção "Interessados Deste Processo" da página pública do processo
   (`processo_detalhado.jsf?id=...`).
3. **Apensado**: abrir o documento "TERMO DE JUNTADA POR APENSAÇÃO" listado nos documentos do
   processo — ele cita explicitamente o número do processo apensado. Não presumir qual é; abrir e
   ler. Depois, confirmar a natureza do processo apensado (ex.: se é mesmo "processo de
   planejamento") abrindo a página pública dele e checando o "Assunto Detalhado".
4. **Aquisição ou Serviço**: olhar o campo **"Assunto Detalhado"** do processo (não do
   apensado). Se contiver a palavra "aquisição", marcar (X) Aquisição; caso contrário, (X)
   Serviços.
5. **Solicitação nº**: abrir o primeiro documento do tipo **"RELATÓRIO DETALHADO DE REQUISIÇÕES
   DO PROCESSO"** (normalmente é o documento 1, mas confirmar pela lista de documentos). Dentro
   dele, citar a **primeira requisição listada** (ex.: "REQUISIÇÃO DE MATERIAIS - Nº 3053/2026"),
   acrescentando "e demais" se houver mais de uma. No campo entre parênteses, no lugar de "às
   fls." (que é numeração da Procuradoria, não existe ainda nesta fase), usar **"(documento N)"**
   — o número do próprio documento do relatório de requisições dentro do processo SIPAC.
6. **Modalidade, tipo de julgamento, objeto e valor**: vêm do Edital/Termo de Referência já
   revisados (cabeçalho do Edital normalmente traz "CRITÉRIO DE JULGAMENTO" e "VALOR TOTAL DA
   CONTRATAÇÃO" prontos).
7. **Versão do modelo AGU usada**: aparece no rodapé do próprio Termo de Referência/Edital (ex.:
   "Termo de Referência - COMPRAS - SISTEMA DE REGISTRO DE PREÇOS - Atualização: dezembro/2025").
   Copiar literalmente dali — **não reaproveitar a versão de outro processo** (ex.: "Serviços sem
   dedicação exclusiva" só se aplica a processo de serviço, não de aquisição — erro já cometido
   na primeira tentativa deste modelo e corrigido).
8. **Relatório de Alterações - Minutas da AGU**: é um tipo de documento próprio que aparece na
   lista de documentos do processo quando existe. Citar como "documento N do processo" (o número
   de ordem dele na lista).
9. **SEI**: a UFRN não usa SEI — esse campo fica sempre em branco (confirmado pelo próprio
   exemplo real assinado).

---

## 3. Geração do PDF

Sem `pdftoppm`/LibreOffice-HTML confiável neste ambiente para replicar o layout com precisão;
gerar diretamente com `pymupdf` (`fitz`), desenhando os quadros (`page.draw_rect` com `fill` cinza
claro para a faixa de título) e o texto (`page.insert_text`/`insert_textbox`). Fontes base a
usar: `"helv"` (normal), `"hebo"` (negrito), `"heit"` (itálico) — nomes de fonte não-padrão (ex.
`"helv-bold"`) ou caracteres fora do Latin básico (✔, –) falham silenciosamente ou geram "?" —
usar "-" ou "( X )" no lugar de checkmarks, e hífen normal no lugar de travessão/en dash.

Script de referência gerado nesta sessão (não commitado no repo — específico do processo testado,
mas serve de base para adaptar): construção via classe `Writer` que escreve linha a linha e
controla `y` manualmente, mais funções `section_box_start`/`section_box_end` para os quadros.

---

## 4. Correção à técnica de paginação do SIPAC (atualiza `CLAUDE.md`, seção 12)

A seção 12 do `CLAUDE.md` registra a paginação de resultados como "pouco confiável via POST".
Descoberta nesta sessão: **funciona**, desde que a página 2 em diante seja enviada para
`/public/jsp/processos/processos.jsf` (não para `/public/jsp/portal.jsf`, que é o endpoint correto
só para a primeira busca). O formulário de resultados (`documentoForm`) tem, de fato, um
`<form ... action="/public/jsp/processos/processos.jsf">` — postar para o endpoint errado faz o
servidor devolver sempre a página 1 (ou erro), dando a falsa impressão de que a paginação não
funciona.

Passos que funcionam:
1. Buscar normalmente (`portal.jsf`), pegar o `javax.faces.ViewState` da resposta.
2. Para cada página seguinte, `POST` para `processos.jsf` reenviando todos os campos ocultos da
   página anterior (`TIPO_PROCESSO`, `CLASSIFICACAO_CONARQ`, `contextoLicitacaoContratos`, etc.)
   mais `documentoForm:j_id_jsp_377120508_26=<índice da página, 1-based>` (o nome exato do campo
   select de página pode variar; conferir no HTML retornado) e o `ViewState` mais recente.
3. Repetir, atualizando o `ViewState` a cada resposta, até achar o resultado ou esgotar as
   páginas.

Vale atualizar o `sipac_client.py` (função `buscar_processos_por_tipo`) para já paginar sozinho
usando essa técnica, em vez de só trazer a primeira página.

---

*Primeiro registro: 09/09/2026, após validar com o processo 23077.121155/2026-38. Ainda não
testado em processo de Contratação Direta (Dispensa/Inexigibilidade) nem em caso sem Relatório de
Alterações único — ajustar quando aparecer um caso desses.*
