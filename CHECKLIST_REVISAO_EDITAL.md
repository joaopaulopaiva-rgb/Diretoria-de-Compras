# Checklist de Revisão — Edital e Relatório de Itens/Preços

Rascunho v1, construído a partir da leitura de 5 editais reais da UFRN (com seus anexos de itens/preços), lidos por completo em agosto/2026:

- 23077.026008/2026-55 — Pregão SISRP 90009/2026 — material para manutenção de bens imóveis
- 23077.018481/2026-69 — Pregão 90006/2026 — material químico controlado
- 23077.031140/2026-89 — Pregão SISRP 90010/2026 — serviços contínuos de controle de pragas
- 23077.005397/2026-85 — Pregão SISRP 90001/2026 — serviços contínuos de empresa especializada (apoio a eventos)
- 23077.031726/2026-43 — Pregão SISRP 90012/2026 — gêneros alimentícios

**Como este documento deve ser usado**: antes de você assinar um edital, ou antes de aprovar um relatório de itens a licitar, eu reviso contra os itens abaixo e reporto achados — nunca corrijo nada sozinho no documento oficial. "Vamos aprimorando com o tempo" — cada rodada de revisão real deve alimentar este checklist com casos novos.

**Formato de retorno da revisão**: eu só reporto o que tiver pendência/achado. Itens do checklist que passaram sem problema não aparecem na resposta — nada de tabela "ok/ok/ok" item por item.

**Técnica de leitura (crítico — aprendido em 26/08/2026)**: os modelos AGU/SGD trazem cláusulas alternativas em **vermelho e/ou tachado** — texto nessa formatação significa que aquele trecho **vai sair** (não foi mantido na versão final). Extração de texto puro (ex. `pypdf`) apaga cor e tachado e mostra as duas alternativas lado a lado como se nenhuma tivesse sido escolhida — isso gera falso positivo sistemático de "cláusula não resolvida". Para revisar corretamente: extrair o PDF preservando cor de fonte e detectando tachado (linha fina sobreposta ao texto — `pymupdf`/`fitz` com `get_text("dict")` + `get_drawings()`, já que `pdftoppm`/poppler não está disponível neste ambiente), montar duas versões (texto limpo = spans não riscados; texto riscado = spans riscados) e revisar a versão limpa. Só reportar como "não resolvido" o que sobrar ambíguo/quebrado *na versão limpa* (ex.: frase cortada no meio porque o tachado foi mal aplicado, ou as duas alternativas tachadas ao mesmo tempo deixando a cláusula vazia).

---

## Parte 1 — Revisão do Edital

### 1.1 Estrutura e conformidade com o modelo AGU
- [ ] O edital segue a estrutura do modelo oficial da AGU (cláusulas na ordem e com o conteúdo esperado)?
- [ ] Alguma cláusula do modelo foi removida ou alterada substancialmente sem justificativa nos autos?
- [ ] Modalidade (Pregão/SRP), critério de julgamento e regime de execução estão coerentes entre capa, corpo do edital e Termo de Referência anexo?

### 1.2 Base legal citada
- [ ] Nenhuma referência à **Lei 8.666/93** (revogada) — achado sistemático em Dispensa/Inexigibilidade segundo `ANALISE_PROCESSOS.md`; vale checar mesmo em Pregão.
- [ ] Se citar Decreto 11.462/2023 art. 3º (justificativa de SRP), o inciso citado (I, II ou V) é coerente com a natureza real do objeto?
- [ ] Se vedar consórcio, há justificativa própria no processo (art. 15, *caput*, Lei 14.133/2021 exige motivação) — não basta citar os Acórdãos TCU padrão sem contexto do caso concreto.
- [ ] Se dispensar IRP, cita art. 86 §1º da Lei 14.133/2021 + art. 9º §2º do Decreto 11.462/2023, e a justificativa ("órgão único") é real?

### 1.3 Consistência interna
- [ ] Número do processo, número do Pregão/SISRP, UASG e datas são os mesmos em todas as páginas/anexos onde aparecem?
- [ ] Valor total do edital bate com o valor total do Relatório de Materiais e Serviços com Preços Estimados?
- [ ] Prazos (impugnação, esclarecimento, entrega de propostas) estão corretos e não conflitam entre si?
- [ ] CEP/endereço da UFRN é o mesmo em todos os documentos (edital, TR, Ata, Contrato)? Achado real: já vi divergência de CEP entre Ata e os demais documentos do mesmo processo.
- [ ] **Resíduo de "contratação direta" na Ata/Contrato de Pregão**: a minuta da Ata de Registro de Preços traz frases como "não será admitida a adesão... decorrente desta licitação **ou desta contratação direta**" — em processo de Pregão, a parte "ou desta contratação direta" é resíduo do modelo de Dispensa/Inexigibilidade e deveria ter sido tachada/removida junto com o resto. Já visto em 2 processos diferentes (Pregão 90018/2026 e 90029/2025) — parece falha recorrente na hora de gerar a minuta, vale checar sempre.

### 1.4 Aspectos redacionais (Português)
- [ ] Ortografia, concordância verbal/nominal, clareza.
- [ ] Termos técnicos usados de forma consistente (não trocar nome do mesmo item entre uma cláusula e outra).

### 1.5 O que eu NÃO decido sozinho
- [ ] Qualquer desvio do modelo AGU sem justificativa clara nos autos: **sinalizo, não presumo motivo e não corrijo**.
- [ ] Qualquer questão jurídica de mérito (ex.: se a vedação de consórcio está bem fundamentada no caso concreto): **aponto a ausência/fragilidade, decisão final é sua ou do jurídico**.

---

## Parte 2 — Revisão do Relatório de Itens/Especificação com Preços

### 2.1 Regra fixa (sua instrução)
- [ ] **Nenhuma ocorrência de "UASG" ou "DL" dentro do texto de "Especificação do Material" de qualquer item.** Essas palavras são normais em cabeçalhos administrativos do relatório (identificação do órgão) — o problema é só se aparecerem *dentro* da descrição técnica de um item, o que indicaria erro de copiar/colar de outro campo do sistema.
  - Testado nos 5 processos da amostra: 0 ocorrências dentro de especificação. Regra confirmada como viável de checar automaticamente.

### 2.2 Consistência interna do item (achado real, vira regra)
- [ ] O código **CATMAT citado dentro do texto da especificação** é idêntico ao campo oficial **CATMAT/CATSER** declarado logo abaixo do item? (achei 1 divergência real em 130 pares checados — processo 23077.026008/2026-55, item 24)
- [ ] A **unidade de medida do título do item** (ex.: "870 ML") bate com a unidade usada no corpo da especificação (ex.: não pode virar "730 gramas")? Mesmo achado do ponto acima, mesmo item — vale checar os dois juntos, costumam andar em par.
- [ ] Quantidade, valor unitário e valor total (Quant. × Valor Unit. = Valor Total) batem aritmeticamente?
- [ ] **CATMAT idêntico entre itens tecnicamente diferentes** (achado novo, padrão recorrente): já vi o mesmo CATMAT/CATSER usado em 2-3 itens de um mesmo Termo de Referência que descrevem produtos fisicamente distintos (ex.: Access Point Indoor 2x2:2 / Indoor 4x4:4 / Outdoor 2x2:2, todos com CATMAT 393277; ou monitores de tamanhos diferentes com o mesmo código). Pode ser catalogação genuína do catálogo oficial, mas o padrão se repete o bastante para sempre reportar como pendência de verificação quando 2+ itens de especificação diferente compartilham CATMAT.

### 2.3 Especificação contraditória ou ultrapassada
- [ ] A especificação cita norma técnica (ABNT NBR, etc.) — é a norma vigente, não uma revisão substituída?
- [ ] Itens de natureza semelhante dentro do mesmo relatório têm exigências coerentes entre si (ex.: mesma faixa de validade mínima para produtos análogos, sem uma exigência mais rígida num item e mais frouxa noutro sem razão aparente)?
- [ ] A especificação exige algo que o próprio texto depois contradiz (ex.: pede characteristic X num trecho e Y incompatível noutro)?

### 2.4 Direcionamento indevido a marca
- [ ] Toda citação de marca vem acompanhada de "ou similar"/"ou equivalente"? (padrão observado como correto nos 5 casos lidos — nenhuma exclusividade de marca encontrada)

### 2.5 Qualidade da pesquisa de preço
- [ ] A fonte da cotação está declarada (Painel de Preços, pesquisa direta com fornecedor, mídia especializada)?
- [ ] Nenhuma cotação usada tem mais de 6 meses de antecedência da divulgação do edital — regra aplicada a **qualquer fonte** de cotação, não só pesquisa direta com fornecedores (art. 23, §1º, IV, Lei 14.133/2021 é a base legal explícita só para pesquisa direta; para as demais fontes, mesmo prazo tratado como padrão interno da Diretoria de Compras, por decisão sua).

### 2.6 Português na especificação
- [ ] Ortografia, unidades de medida escritas de forma padronizada, sem ambiguidade.

---

## Casos reais que alimentaram este checklist

| Achado | Processo | Onde |
|---|---|---|
| CATMAT do corpo (612390) ≠ CATMAT/CATSER oficial (319588) | 23077.026008/2026-55 | Relatório de Preços, item 24 |
| Unidade do título (870 ML) ≠ unidade do corpo (730 gramas) | 23077.026008/2026-55 | Relatório de Preços, item 24 (mesmo item acima) |

---

## Validado por você em 19/08/2026

1. Regra de "6 meses" (item 2.5) vale para qualquer fonte de cotação, não só pesquisa direta.
2. Retorno da revisão é só pendência/achado (já refletido na seção "Como este documento deve ser usado").
3. Item 2.3 ("especificação ultrapassada") fica como está — mais teórico por enquanto, a calibrar quando aparecer caso real.

---

*Rascunho v1 — 19/08/2026. Ver `BASE_LEGAL_PREGAO.md` e demais `BASE_LEGAL_*.md` para a base jurídica usada como pano de fundo desta revisão.*
