# Análise de Conteúdo dos Processos de Compra — UFRN

Referência de análise construída a partir da leitura completa (documentos + movimentações, não só datas de marco) de uma amostra de processos reais no SIPAC público, um por um. Objetivo: servir de apoio quando a pessoa perguntar sobre um processo novo — "esse prazo está normal?", "esse caso deveria ir de Pregão ou Dispensa?", "que documento costuma vir depois desse?", "esse valor está dentro do esperado?".

Este documento **complementa o `CLAUDE.md`** (que descreve a estrutura confirmada por auditoria anterior, ~20 processos/caminho) com uma amostra mais ampla e com achados sobre conteúdo real: prazos observados, linguagem de justificativa, padrões de precificação, exceções e sinais de alerta. Quando este documento contradiz ou refina algo do `CLAUDE.md`, isso é sinalizado explicitamente.

## Metodologia

- Amostra tirada de `data/processos.json` (~795 processos classificados por caminho, levantamento histórico jan/2024–ago/2026), com seed fixa para reprodutibilidade.
- Tamanho da amostra ajustado à população real de cada caminho: **30** para Pregão, Dispensa e Adesão SRP; **25** para Inexigibilidade; **13** (população total confirmada) para Concorrência; **2** (população total conhecida até agora) para Contrata+Brasil.
- Cada processo foi lido por completo: todos os documentos substantivos (despachos de autorização, autorizações formais, notas técnicas/informativas, pareceres, termos, notas de empenho, documentos de valor/pesquisa de preço), não só os títulos — incluindo abertura do Termo de Juntada por Apensação e, quando necessário, resolução do id SIPAC do processo de Planejamento apensado (busca por Tipo de Processo=314 com bisecção de janela de datas, já que a busca direta por número não funciona no SIPAC público).
- Trabalho paralelizado em 10 sub-agentes (2 por caminho para Pregão/Dispensa/Adesão SRP/Inexigibilidade, 1 para Concorrência, 1 para Contrata+Brasil), cada um instruído a nunca presumir conteúdo de documento que falhou ao ler e a sinalizar qualquer inconsistência em vez de adivinhar.
- Data da leitura: agosto/2026.

**Como usar**: cada seção por caminho tem prazos observados (não normativos — são o que foi visto na amostra, com exemplos concretos citando número de processo), padrões de precificação/negociação, exceções reais encontradas, e sinais de alerta. A seção final consolida perguntas em aberto que precisam de confirmação humana antes de virarem "fato" no painel.

---

## 1. Pregão (30 processos lidos)

### Fluxo confirmado + achado metodológico importante

O modelo do `CLAUDE.md` (seção 3) se confirma, com uma descoberta operacional relevante: quando um processo já passou da fase de Planejamento, o `id_atual`/número que aparece como "o processo" nas fontes de dados é o do **Pregão**, com número **diferente** do Planejamento original — e o Termo de Juntada por Apensação sempre confirma a direção ("apensar ao presente processo nº [PREGÃO] o(s) processo(s) nº(s) [PLANEJAMENTO]").

**Achado novo, não documentado antes**: o processo de Pregão recebe uma **cópia em lote** do DFD/ETP/TR do Planejamento, carimbada com a data de abertura do próprio Pregão — não é a fonte real dessas datas. Exemplo: um Pregão mostrava FORMALIZAÇÃO DA DEMANDA, ETP e TR todos com a mesma data (23/04/2024), enquanto o Planejamento genuíno mostrava os mesmos artefatos com datas reais espalhadas entre 26/01 e 10/04/2024. **Isso reforça — com evidência concreta — a regra de nunca misturar a fonte** (CLAUDE.md seção 2): usar sempre as datas do processo de Planejamento para DFD/ETP/TR, mesmo que apareçam "de novo" no Pregão.

A apensação normalmente ocorre **perto do fim da Elaboração de Edital** (junto com Portaria de Pregoeiro, Minuta de Edital/ATA e Lista de Verificação), não no envio inicial DPGC→DFI como a posição da sub-etapa na tabela do CLAUDE.md poderia sugerir.

**Exceção real confirmada**: em pelo menos 1 processo (material farmacológico), a fase interna inteira aconteceu dentro do próprio processo de Planejamento, sem nunca se desdobrar em Pregão — porque a Diretoria de Compras abandonou a via de pregão no meio do caminho (fracassos recorrentes de itens) e reverteu para contratação direta. É um caso real de mudança de caminho no meio do processo (CLAUDE.md seção 15, ainda "em aberto").

**Apensação em sentido inverso** (obras/engenharia): num processo de elevador, é o próprio processo (já numerado como o "principal") que absorve um processo mais antigo como apenso — mecânica de apensação comum entre processos correlatos, não a divisão Planejamento→Pregão.

### Variantes por tipo de objeto

- **TIC** (servidores, storage, redes, software): segue a IN SGD/ME nº 94/2022, com Nota Técnica da STI e Despacho de Instituição de Equipe de Planejamento da Contratação (Integrante Requisitante + Técnico + Administrativo) — etapa extra que não existe no fluxo padrão. Consistentemente mais lento; um dos processos de TIC observados (SaaS de licenciamento) terminou **arquivado** por decisão de não continuidade.
- **Obras/engenharia**: ETP/TR passam pela Superintendência de Infraestrutura (CAOSE, DO, DFO, COPB), com Orçamento Sintético/Analítico, BDI/LDI, ART e SISPP (não SRP) — muito mais lento que o padrão Compras (ver também seção Concorrência, que tem o mesmo padrão de obras).

### Prazos típicos observados

| Sub-etapa | Faixa observada | Nota |
|---|---|---|
| DFD (cadastro → despacho de autorização) | 0–3 dias no caso comum; até 10+ meses com retrabalho/TIC | maiores atrasos são **hiatos entre sub-etapas**, não a duração do ato em si |
| ETP (autorização DFD → autorização ETP) | 2–75 dias | obras/TIC nas faixas mais altas |
| TR (autorização ETP → autorização TR) | 1–46 dias | |
| Lista de Verificação → envio DPGC→DFI | 30–82 dias (estimado via data do Termo de Juntada, ver ressalva) | ver "casos de baixa confiança" — pode superestimar |
| Análise DFI (Nota Pesquisa Preços → Nota IRP) | 1–32 dias | |
| Pesquisa de Preços (Nota IRP → Nota Edital) | 3–33 dias | |
| IRP/Elaboração de Edital (Nota Edital → Certificação Processual) | 1–63 dias | |
| Jurídico — via Parecer Referencial AGU (valor < R$1M) | mesmo dia | atalho recorrente para objetos padronizados de menor valor |
| Jurídico — parecer individualizado AGU (objeto complexo/maior valor) | resposta interna em 1–6 dias; parecer da AGU em si leva 14–18 dias | |
| DFE (Divulgação/Publicação → Homologação) | 30–62 dias sem incidente; mais com impugnação/recurso | |
| **Total (ETP até Homologação)** | ~3 meses (rápido) a ~1 ano (com retrabalho) | |

### Padrões de negociação/precificação

- **Parecer Referencial da AGU** (nº 00006/2025/GERTEC/ELIC/PGF/AGU) dispensa exame jurídico individualizado para contratações abaixo de R$1 milhão com modelos-padrão da AGU — atalho jurídico recorrente em processos de menor complexidade/valor.
- **Fórmula recorrente de justificativa para SRP**: cita incisos I, II ou V do art. 3º do Decreto nº 11.462/2023.
- **Vedação de consórcio**: praticamente todo Edital cita os mesmos três acórdãos TCU (2633/2019, 1.946/2016, 1316/2010) — texto padronizado copiado entre processos.
- **IRP dispensada por "órgão único"**: quando só a UFRN vai consumir a ata, a DFI justifica formalmente (art. 86 §1º Lei 14.133/2021) a não divulgação de IRP — economiza a sub-etapa inteira.
- **Valor final tende a cair após pesquisa de preços real**: um caso caiu ~4,5% do DFD para a Certificação Processual — padrão saudável de ajuste.
- **Sobrepreço detectado e corrigido no ETP**: um processo (picape/veículo) tinha valor de referência 78% acima do mercado real (cotado direto com montadoras); a Coordenadoria de Transportes apontou, e o ETP foi revisado e reautorizado em 13 dias — mostra fragilidade de pesquisas de preço baseadas só em atas de outras IFES sem checagem cruzada de varejo/fabricante.
- **Impugnações e recursos são resolvidos rápido quando bem instruídos**: impugnação por preço inexequível respondida em 6 dias; recurso por não-conformidade técnica resolvido em ~1 semana.
- **Certificação Processual**: em processos de 2024 era assinada localmente pelo Diretor de Compras; em 2025-2026 passou a ser feita remotamente pela "Equipe de Trabalho Remoto de Licitações e Contratos – ETRLIC" da AGU — mudança de governança ao longo do tempo, vale ter em mente ao comparar processos antigos vs. recentes.

### Exceções e variantes encontradas

- Negociação pré-DFD informal e prolongada (ida-e-volta de meses com a unidade requisitante antes do DFD formal existir) — ciclo não capturado pelo modelo de 10 sub-etapas.
- Apensação múltipla: um Termo de Juntada apensou **dois** processos de uma vez ao mesmo Pregão, incluindo um de 3 anos antes (2021) — sugere reaproveitamento de estudo/demanda antiga.
- Pós-homologação segue vivo no mesmo processo: Termo de Desapensação e "Correção de Valor por Índices de Preços" meses depois da Homologação.
- Documento com conteúdo de outro tipo colado por engano (Nota Informativa de "Elaboração de Edital" com texto de "pesquisa de preços para dispensa de licitação") — defeito de forma, vale checar se se repete.

### Sinais de alerta / problema observados

- **Fracasso recorrente de categoria inteira**: Diretoria de Compras registrou formalmente que pregões de material farmacológico têm fracassado repetidamente, motivando reversão para contratação direta — vale investigar se outros processos farmacológicos compartilham o padrão.
- **Retrabalho com interrupção de meses**: um processo divulgado, voltou para pesquisa de preço e minuta de edital, e só foi redivulgado ~6 meses depois — quase 1 ano de duração total.
- **Obras paradas por mais de 1 ano só na etapa de DFD** — mesmo padrão observado em Concorrência (seção 5).
- **Processo represado por falta de equipe técnica interna + greve** — a unidade de manutenção indeferiu a requisição por falta de especialistas, e o redirecionamento para outra diretoria ficou condicionado ao fim de uma paralisação grevista.
- **Estagnação de longo prazo em estágio inicial** (extintores): só 3 documentos em mais de 14 meses, parado na composição da equipe de planejamento.
- **Possível estagnação/discrepância de fase**: pelo menos 1 processo rotulado "Fase Externa (DFE)" tinha trilha documental parada no TR, sem Nota Informativa/Certificação/Parecer/Edital — vale confirmar se é estagnação real ou rótulo desatualizado.

---

## 2. Dispensa de Licitação (30 processos lidos)

### Fluxo confirmado

O padrão dominante se confirma **fortemente e com taxa mais alta que a baseline anterior**: nos 22 processos da amostra que já saíram da fase de Planejamento puro, **100% (22/22) tinham Termo de Juntada por Apensação real** — mais alto que a estimativa anterior de ~15/18 (~83%). **Zero casos da variante minoritária "sem apensação"** apareceram nesta amostra mais ampla (a variante existe — CLAUDE.md documenta 2/20 — só não apareceu nestes 30).

**Achado metodológico**: o número que chega rotulado como "o processo" (fase Homologado/Fase Externa) é sempre o do **Planejamento**, não da Dispensa — a direção do Termo de Juntada é sempre "apensar ao presente processo nº [Dispensa/DFI] o(s) processo(s) nº(s) [nosso Planejamento]". Na prática, a página pública do Planejamento, uma vez apensado, já mostra a listagem **mesclada completa** (DFD/ETP/TR/Autorização + Julgamento + Empenho todos juntos) — não é preciso abrir separadamente o número da Dispensa para ler o conteúdo inteiro.

Fechamento: a esmagadora maioria (>90%) fecha só com Nota de Empenho. Contrato formal aparece em casos pontuais (locação de becas para colação de grau) — sem Termo Aditivo nem Parecer Jurídico visível, diferente do caso "raro" documentado anteriormente no CLAUDE.md.

### Prazos típicos observados

| Sub-etapa | Faixa observada |
|---|---|
| Cadastro do Planejamento → Termo de Juntada (apensação) | 0–31 dias |
| Autorização (DPGC) → Termo de Juntada | mediana ~9 dias |
| Termo de Juntada → Declaração de Disponibilidade Orçamentária | 0–5 dias (ocorre **cedo**, logo após apensação, não no fim como a posição na tabela sugere) |
| Termo de Juntada → Divulgação da Dispensa (quando há) | 7–35 dias |
| Divulgação → Quadro Comparativo/Parecer Técnico | 4–28 dias |
| Quadro Comparativo → Nota de Empenho | 3–69 dias |
| **Ponta a ponta (Ofício/DFD → Empenho)** | **1 a 121 dias, mediana ~20-35 dias** |

Casos mais rápidos (1-6 dias) tendem a ser compras recorrentes/padronizadas de baixo valor (óleo de soja, hortifrutigranjeiros) — mas nesses casos específicos a listagem não mostrava DFD/ETP/Autorização de Formalização separados, então não está 100% confirmado se são de fato mais simples ou se a leitura perdeu documentos (ver casos de baixa confiança).

### Padrões de negociação/precificação

- **Base legal dominante**: art. 75-II Lei 14.133/2021 (baixo valor). Exceção real e relevante: art. 75-III-b (licitação **fracassada**) — Dispensa também é usada como saída de pregões malsucedidos, não só por valor baixo.
- **Linguagem-padrão recorrente**: "baixa complexidade da contratação e o módico valor financeiro envolvido... não ser necessária a aplicação da matriz de alocação de riscos" — aparece quase palavra-por-palavra em ~40% dos processos lidos.
- **Metodologia de pesquisa de preço**: comparação contra registros de compras de outros órgãos públicos, filtro de 12 meses, "Método de cálculo adotado: Mediana" declarado explicitamente.
- **Negociação amarrada a saldo orçamentário**, não só ao menor preço: um caso teve proposta aceita "condicionada ao valor máximo... em virtude de ser o valor que consta como disponível no saldo" da unidade — o teto orçamentário, não o mercado, define o corte.
- **Rejeição técnica fundamentada**: propostas recusadas por não atenderem especificação técnica exigida (ex.: compatibilidade de software/sensor específico) — evidência de negociação/julgamento real, não formalidade.
- **Base legal desatualizada em template**: praticamente todo Parecer Técnico cita "Lei 8.666/93" *e* "art. 75-II da Lei 14.133/2021" na mesma frase — mistura de lei revogada com enquadramento correto, presente sistematicamente. Parece modelo de documento desatualizado, não erro caso a caso — vale reportar para correção do template.

### Exceções e variantes encontradas

- **Fracasso e reapensação a uma Dispensa nova**: um Planejamento tentou seguir por uma Dispensa que fracassou; quase 1 ano depois foi reapensado a uma Dispensa totalmente nova — padrão estrutural real de retrabalho não descrito no modelo original.
- **Apensação em lote**: um Termo de Juntada apensou **quatro** processos de Planejamento de uma vez à mesma Dispensa — a DFI às vezes consolida várias demandas pequenas numa única Dispensa.
- **Mudança de caminho no meio do processo**: um Planejamento começou como Adesão a Ata de Registro de Preços, foi revertido parcialmente para Dispensa, teve orçamento invalidado, foi suspenso aguardando resultado de um Pregão concorrente, e retomou 5 meses depois — caso real de "troca de caminho" (CLAUDE.md seção 15, ainda em aberto).
- **Contrato formal em vez de só Empenho**: locação de becas — Contrato + Convocação + Portaria + Termo de Desapensação final (correção administrativa, não mudança de mérito).

### Sinais de alerta / problema observados

- **Processos aparentemente estagnados por meses**: pelo menos 2 casos com um único documento/movimentação há 5-10 meses sem avanço — candidatos fortes a acompanhamento manual (um deles, contratação de ilustrador, parado há ~10 meses).
- **Perda de prazo administrativo**: um processo foi devolvido para arquivamento por chegar após o prazo-limite de recebimento de propostas, retomado só 5 meses depois com orçamentos atualizados.
- **Empenho fracionado em múltiplas parcelas** sem causa documentada claramente — pode ser normal (fornecedores/itens distintos) ou sinal de problema de planejamento de saldo; vale confirmar caso a caso.
- **Gap sistemático perto da virada de exercício financeiro** (dez/jan): pelo menos 1 caso com 69 dias entre julgamento e empenho atravessando a virada — hipótese de represamento de fim de exercício, não confirmada em texto, mas padrão a observar em outros processos de dezembro.

---

## 3. Inexigibilidade de Licitação (25 processos lidos)

### Fluxo confirmado

Confirma-se com a **taxa de apensação mais alta de todos os caminhos**: 20/20 processos já em execução (Homologado/Fase Interna) tinham Termo de Juntada por Apensação — 100%, batendo com o "quase absoluto" já documentado no CLAUDE.md (que citava 100% numa amostra menor).

**Mesmo achado metodológico da Dispensa**: o número rotulado como "o processo" na fase de execução é, na verdade, o número do Planejamento apensado — o processo de execução real tem outro número, achado sempre no cabeçalho "Consulta do Processo" da própria página. Para achar o Planejamento é preciso resolver o número que aparece como "processo do lote" (não o número citado dentro do Termo de Juntada, que é o da execução).

Bloco de fechamento muito compacto e padronizado: no mesmo dia da apensação (ou +1) saem em sequência Despacho de enquadramento → Relatórios → Quadro Comparativo de Propostas → **Parecer Técnico** (documento central, autoriza formalmente a Inexigibilidade) → Nota de Resumo para Empenhos → Nota de Empenho.

- **Sem Jurídico na maioria (confirmado em ~90% da amostra)** — mas há **exceção real e relevante**: um contrato de serviços postais monopolizados (Correios/ECT) passou por Parecer Jurídico da Procuradoria-Geral Federal/AGU com 10 ressalvas formais. Objetos de execução continuada/valor recorrente anual parecem ser o gatilho para exigir Jurídico, mesmo em Inexigibilidade.
- **Sem DFE, confirmado universalmente.**
- **Fecha quase sempre com Nota de Empenho**, mas contratos de execução continuada (Correios, credenciamento de leiloeiros) seguem até **Contrato Administrativo formal** + Publicação D.O. + Portaria de Fiscal — desfecho não previsto no modelo de sub-etapas original, mas recorrente quando o objeto é continuado.

### Prazos típicos observados

| Sub-etapa | Faixa observada |
|---|---|
| Ofício/Solicitação → DFD | 1–96 dias |
| DFD → ETP/Mapa de Riscos | 0–36 dias |
| Autorização de Contratação Direta → Apensação | 3–140 dias (maior gap: manutenção de equipamento técnico específico) |
| Apensação → Parecer Técnico/Quadro Comparativo | **sempre no mesmo dia** — o padrão mais consistente de todo o caminho |
| Apensação → Nota de Empenho | 1–18 dias |
| Empenho → Contrato (quando há) | 9 dias a **9,5 meses** (contrato de execução continuada — forte sinal de alerta) |

### Padrões de negociação/precificação

- **Carta de Exclusividade** é o documento-chave em ~65% dos casos (Art. 74, I) — emitida pelo próprio fabricante/distribuidor exclusivo, ou por associação de classe (ex.: ABIMED atestando representação exclusiva de marca estrangeira no Brasil).
- **Art. 74, IV — credenciamento de leiloeiros públicos**: padrão de precificação **simbólico, R$ 0,01** — o leiloeiro é remunerado por comissão dos arrematantes, não pela UFRN. Visto em processos originados da mesma lista de credenciamento (sugere que colocados anteriores da lista foram pulados/recusaram).
- **Art. 74, II — profissional de notório saber (setor artístico)**: usa "Justificativa" de notória especialização + Proposta de Produto do artista, não Carta de Exclusividade — base documental diferente do padrão de fornecedor exclusivo.
- **Software/licenciamento é a categoria mais comum** na amostra (~30% dos casos) — licenças/renovações com fornecedor único.
- **Categoria de exclusividade explica valor**: faixa de R$ 0,01 (leiloeiro) a R$ 32.367,00 (manutenção de equipamento especializado) nos casos avulsos; contrato anual de serviços postais monopolizados chega a R$ 109.938,11/ano — categoria de valor recorrente mais alto do caminho.
- **Ruído a filtrar reafirmado**: Termo de Desapensação como correção administrativa pontual, confirmado empiricamente (apensação errada às 18h, corrigida às 9h do dia seguinte).
- **Padrão novo observado**: Termo de Desapensação também aparece **depois** de contratos formais concluídos (2 casos, mesma data) — pode ser fechamento/arquivamento de rotina, não necessariamente correção de erro. Hipótese com poucos casos, não generalizar ainda.

### Exceções e variantes encontradas

- Carta de Exclusividade emitida **meses antes** do Ofício formal de abertura — indício de que a unidade já articulava a compra informalmente antes de formalizar via DPGC.
- TR com múltiplas versões (3-4 revisões) em processos de baixo valor nominal — retrabalho desproporcional ao valor da contratação.
- Um caso de apensação dupla anômala: dois processos de Planejamento diferentes apensados no mesmo dia ao mesmo processo de execução, com Desapensação e nova Apensação no mesmo dia — correção pontual, mas a relação exata entre os dois planejamentos não ficou clara na leitura.
- Um desmembramento: processo tratando só de componentes físicos (dongles USB) porque a licença de software já tinha sido comprada em processo separado, por orientação de compras internacionais.

### Sinais de alerta / problema observados

- **Gargalo do lado da unidade requisitante, não da DPGC**: um processo teve ~10 meses de tramitação sem fechar TR/Autorização, com 5 meses de silêncio da unidade requisitante entre uma cobrança da DPGC e a resposta — vale distinguir esse tipo de atraso (responsabilidade da unidade demandante) de atraso interno da Diretoria de Compras.
- **Contrato de execução continuada com atraso grande pós-empenho**: ~9,5 meses entre Empenho e assinatura de Contrato — maior atraso pós-empenho observado no caminho.
- **Template desatualizado sistemático** (mesmo padrão da Dispensa): Pareceres Técnicos citam Lei 8.666/93 junto com o enquadramento correto em art. 74 da Lei 14.133/2021.
- **Enquadramento legal a confirmar**: um workshop de capacitação de baixo valor foi enquadrado no Art. 74, Inciso III (tipicamente reservado a serviços técnicos especializados de natureza singular), quando o Inciso I (fornecedor exclusivo) poderia ser mais apropriado — risco baixo dado o valor, mas padrão a observar.
- **Discrepância de mapeamento processo↔id** encontrada num item da amostra de trabalho (o número indicado não correspondia ao processo de execução real, e sim a um dos apensados) — sinalizado para quem gerar amostras futuras a partir da mesma base de dados.

---

## 4. Adesão a Ata de Registro de Preços — SRP (30 processos lidos)

### Fluxo confirmado

**Confirma-se como o caminho mais limpo e consistente de todos** — nenhum dos 30 processos precisou de resolução de id separada (o processo rastreado já É o Planejamento, com o documento de fechamento real dentro dele, exatamente como o CLAUDE.md descreve na seção 4.3).

Sequência real observada (por movimentação de unidade):
1. Unidade requisitante → **DPGC**: chega Ofício/E-mail, às vezes já com Carta de Aceite do fornecedor pré-negociada.
2. **DPGC** monta DFD + ETP + Justificativa + SICAF + Consulta TCU + **Pesquisa de Preço** (Painel de Preços) → emite **Autorização de Formalização** (sempre com Grupo de Material, UASG gerenciadora, pregão de origem, item, marca, quantidade, valor unitário) → encaminha à DFI.
3. **DFI** analisa Documento Comprobatório de Licitação e emite a **Autorização de Adesão a Ata de Registro de Preços** — repete os mesmos dados de precificação, agora endereçada à Pró-Reitora de Administração.

Sem Jurídico, sem DFE, sem pesquisa de preço "do zero" — confirmado universalmente.

**Exceção de nomenclatura recorrente (não é exceção rara)**: em vários processos (não isolados), o documento de fechamento com o teor idêntico ao padrão foi protocolado com o tipo **"DESPACHO"** genérico, não com o tipo formal "Autorização de Adesão a Ata de Registro de Preços" — mesma função, rótulo diferente. Quem procura só pelo tipo de documento oficial perde esses casos.

### Prazos típicos observados

Do início (chegada em DPGC) até o fechamento (Autorização de Adesão em DFI):

| Faixa | Interpretação |
|---|---|
| 1–7 dias | maioria dos casos "limpos" — mediana informal da amostra |
| 8–34 dias | casos com alguma retificação ou fila normal de DFI |
| >100 dias (outliers) | sempre por causa específica documentada (ver Exceções) |

Dentro do ciclo, a etapa DFI (Documento Comprobatório → Autorização de Adesão) costuma levar **1 dia** — desvios de 8, 14 ou 30 dias são exceção, não norma, e nem sempre têm despacho explicando a causa (ver Sinais de Alerta).

### Padrões de negociação/precificação — o achado mais forte de toda a leitura

- **Validação de preço = Painel de Preços, comparando contra a ata, nunca cotação nova.** A Autorização de Formalização sempre declara "o valor é compatível com os valores registrados em aquisições congêneres no Painel de Preços".
- **Achado replicado de forma independente em múltiplos processos**: o valor unitário efetivamente aderido coincide, com frequência notável, com o "Menor" preço encontrado no Painel de Preços — não a média nem a mediana. Isso é um padrão de negociação forte o suficiente para usar como referência: **a Diretoria de Compras busca sistematicamente a ata de menor preço disponível**, não apenas "dentro da média".
- **Limite de 50% da quantidade homologada por não-participante**: confirmado explicitamente em pelo menos 1 processo — DPGC devolveu pedido por exceder o teto de adesão de não-participante (50% do quantitativo homologado no pregão de origem). Regra prática a ter em mente ao avaliar se uma quantidade pedida é "normal".
- **Faixa de valores unitários**: de centavos (desinfetante, R$1,67) a milhares (notebooks R$3.188-6.890, licenças de software R$33.253,13) — a maioria dos itens de consumo fica entre R$20-500/unidade.
- **UASGs gerenciadoras muito variadas** (institutos federais, universidades, órgãos militares, TREs) — UFRN adere amplamente sem restrição de esfera/tipo de órgão gerenciador.
- **Categorias de material mais comuns**: hortifrúti/alimentos, utensílios/paletes, limpeza, manutenção de imóveis, material hospitalar, máquinas/equipamentos energéticos, TIC, mobiliário acadêmico, instrumentos de medição.
- **Negociação por item isolado de um lote maior** exige justificativa adicional de economicidade em vários casos — não basta querer só 1 item de um lote de 10, precisa justificar.

### Exceções e variantes encontradas

- **Adesão negada pelo órgão gerenciador, com reabertura completa do ciclo**: 1ª tentativa negada e arquivada; processo reaberto meses depois com nova Carta de Aceite/DFD/ETP (fornecedor e valor diferentes) e concluído com sucesso — ciclo total de mais de 4 meses, mas cada tentativa individual foi rápida.
- **Item não cadastrado no sistema bloqueia a adesão** — problema de cadastro interno do SIPAC, não dependência externa, mitigável proativamente.
- **Órgão gerenciador não responde no prazo** — bloqueio por dependência externa sem SLA, risco real de travar indefinidamente.
- **Pré-exigência de ETP + Justificativa da AGU introduzida institucionalmente em meados de julho/2024** — processos concluídos antes dessa data não têm ETP formal separado; processos depois têm. Útil para calibrar expectativa ao olhar processos por data.
- **Variante TIC** (software, notebooks): rito mais robusto (Equipe de Planejamento, Nota Técnica, TR em vez de só ETP, Mapa de Riscos) por força da IN SGD/ME nº 94/2022 — mas não necessariamente mais lento.
- **Rejeição pelo órgão gerenciador por erro de documentação** (Carta de Anuência com UASG incorreta) — episódio que, somado a retrabalho, esticou um ciclo para ~245 dias.
- **Retificações por limitação técnica do próprio SIPAC**: sistema só aceita quantidades inteiras, forçando arredondamento; divergências de centavos entre Carta de Aceite e valor homologado geram ciclos de correção.
- **Segunda adesão ao mesmo item já usado antes pela UFRN** — nesse caso o processo seguiu até Nota de Empenho dentro do próprio processo de adesão.

### Sinais de alerta / problema observados

- **Preço ~4x acima da mediana do Painel de Preços, mas aceito com justificativa específica** (heterogeneidade do código de material, ex. "serra fita" cobrindo desde modelos pequenos a industriais) — padrão a vigiar se aparecer sem justificativa tão clara em outros casos.
- **Reaproveitamento de texto/template sem atualização**: pelo menos 1 "Justificativa da vantagem da adesão" mencionava o objeto de *outro* processo (copy-paste não revisado) — problema de qualidade documental, não de mérito, mas merece atenção em revisão.
- **Descrição de item divergente entre a solicitação original e o documento de fechamento** (modelo/fabricante diferente do pedido, mesma quantidade/valor) — risco de confusão na hora do empenho/recebimento físico do material.
- **Fornecedor com SICAF "Inativo"/impedimento aparecendo no meio do processo**, sem explicação textual clara da troca para outro fornecedor — sem evidência de má conduta, mas trilha documental pouco explícita.
- **Lacunas de meses sem movimentação aparente** em pelo menos 2 processos, sem despacho explicando a causa — candidatos a acompanhamento manual.

---

## 5. Concorrência (13 processos lidos — população total confirmada)

### Fluxo confirmado

Confirmado por "Assunto Detalhado" que os 13 processos são contratações originais (não acessórios pós-award). O modelo de sub-etapas 1-4 dentro do próprio processo (sem apensação de planejamento separado, diferente dos demais caminhos) se confirma para 10/13 processos "de obra" propriamente ditos.

**Duas exceções estruturais reais**:
- Uma concessão onerosa de bem público (não é obra de engenharia clássica) não passa pelo CAOSE/INFRA em nenhum momento — tramita inteiramente pela DPGC, seguindo o caminho "padrão" não-obra.
- Quando o demandante não é a própria Infraestrutura (ex.: uma diretoria de comunicação pedindo manutenção de torre), o DFD nasce fora do CAOSE/INFRA, via DPGC, só migrando para Infraestrutura na fase de projeto técnico.

**Achado metodológico importante — "fase externa invisível" no SIPAC público**: em nenhum dos 12 processos de obra aparece documento de Edital, Termo de Julgamento ou Homologação na tabela pública de Documentos. Mas as movimentações de pelo menos 3 processos mostram claramente que já passaram por Fase Externa → Procuradoria → Contratos-Formalização — ou seja, aparentemente já homologados, sem que nenhum documento correspondente apareça na listagem pública. Duas hipóteses não confirmadas: (a) esses documentos vivem só no PNCP (a Lei 14.133/2021 exige publicação lá) e não no SIPAC; (b) existe um processo-filho específico para a licitação que não foi capturado nesta leitura. **Recomendação prática: tratar o campo "fase" de Concorrência como aproximado, e usar as movimentações (não só a lista de documentos) como sinal mais confiável do estágio real.**

**Variante de fundação de apoio**: pelo menos 1 processo teve a fase de licitação inteira conduzida por uma fundação de apoio (FUNPEC) via regime jurídico próprio (Decreto nº 8.241/2014), não diretamente pela Lei 14.133/2021 — processo literalmente movimentado para a unidade da fundação por meses.

### Prazos típicos observados

| Intervalo | Faixa observada |
|---|---|
| DFD → ETP | 5 a 321 dias (típico 49–122) |
| ETP → TR | 6 a 433 dias (típico 22–72) |
| DFD → TR (total) | 11 a 513 dias (típico 73–154) |
| TR → Fase Externa | ~39–46 dias |
| TR → Contratos (fase externa completa) | ~70–140 dias nos casos rastreáveis |

**Concorrência é, de longe, o caminho mais lento e mais disperso** — não há um "prazo típico" único e confiável; outliers de vários meses causados quase sempre por espera de dotação orçamentária ou re-escopo de projeto, não pela burocracia do ato em si.

### Padrões de negociação/precificação

- Valores das obras variam de ~R$130 mil (fornecimento/instalação de equipamento elétrico, não obra civil) a mais de **R$51 milhões** (obra multi-campus) — Concorrência lida com as maiores cifras de todos os caminhos investigados.
- **BDI padronizado e aparentemente fixo**: 22,69% idêntico entre processos distintos (Lucro 6,90% + Administração Central 4,00% + Taxa de Risco 1,27% + Custo Financeiro 1,23% + Tributos 7,15%) — todos os orçamentos usam SINAPI como fonte de referência.
- Prazo de execução de obra observado: 180-450 dias dependendo do porte (obra multi-campus na ponta mais longa).
- Um caso concreto de negociação: proposta vencedora ~18% abaixo do valor estimado (via fundação de apoio).

### Exceções e variantes encontradas

- Concessão onerosa (não-obra) cita **Lei 8.666/93 revogada** em vez da Lei 14.133/2021 — possível minuta desatualizada reaproveitada.
- **Reabertura pós-distrato**: pelo menos 1 processo é a recontratação da parte remanescente de uma obra cujo contratado anterior abandonou o canteiro (distrato unilateral) — evidência direta de obra fracassada/abandonada.
- Documentos históricos antigos (2009, 2019, 2020, 2021) aparecem embutidos em pelo menos 3 processos sem um Termo de Juntada explícito formal ligando-os — pode ser upload de material de referência, não apensação formal; **hipótese do CLAUDE.md seção 4.4 (14/16 processos com apensação de planejamento embrionário anterior) permanece só parcialmente confirmada** — vale investigação futura dedicada.

### Sinais de alerta / problema observados

- **Obras paradas por mais de 1 ano numa única sub-etapa** (2 casos: um sem TR autorizado após mais de 17 meses desde o ETP; outro com gap de 433 dias entre ETP e TR por espera de dotação orçamentária) — padrão consistente de risco em obras, reforça o achado equivalente já visto em Pregão de obras.
- **Evidência direta de obra fracassada/abandonada** (contratado anterior abandonou o canteiro) — vale mapear se há outros casos similares no universo maior de Concorrência.
- **Rótulo de fase desatualizado** para pelo menos 3/13 processos (ver achado metodológico acima) — não confiar cegamente no campo "fase" para Concorrência sem checar movimentações.

---

## 6. Contrata+Brasil (2 processos lidos — primeira leitura real, exploratória)

**Importante**: esta seção é rascunho, não padrão confirmado — apenas 2 processos, mesma unidade (Diretoria de Compras), mesmo servidor responsável, e mesmo fornecedor MEI final nos dois casos. Tratar como hipótese inicial a validar com mais casos antes de generalizar.

### O que foi encontrado

- **Não existe tipo de processo próprio no SIPAC para Contrata+Brasil** — usa o mesmo tipo genérico "PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO (33.00)" dos demais caminhos. O único sinal de que é Contrata+Brasil é o sufixo no "Assunto Detalhado" e o conteúdo dos despachos.
- **Sem apensação de planejamento** — mais radical do que o esperado: tudo roda num **único processo**, do pedido inicial até a Nota de Empenho, sem DFD/ETP/TR próprios (esses vêm prontos da plataforma federal).
- Estrutura documental observada: Ofício da unidade → tela "PROPOSTAS" (print da plataforma Contrata+Brasil, com campo "Apenas MEI: Sim" e contagem de "Empresas compatíveis no sistema") → Despacho Informativo citando a **Instrução Normativa SEGES/MGI nº 52/2025** → Despacho de indicação da proposta vencedora → (quando há problema) novo ciclo de renegociação → Despacho de Encaminhamento citando o "Id da contratação no PNCP" → **Nota de Empenho** (Sistema COMPRASNET-ME) → Requisição de Serviços lançada **depois** do Empenho (ordem invertida da usual).

### Divergência importante a confirmar

Nos 2 processos lidos, a Nota de Empenho cita **Modalidade: INEXIGIBILIDADE (Lei 14.133/2021, Art. 74, IV)** — não o **art. 75 (dispensa)** que era a base legal esperada pelas fontes públicas genéricas sobre o programa. Com apenas 2 casos (mesmo fornecedor, mesmo tipo de serviço), não dá para saber se isso é a regra geral do programa ou uma peculiaridade desses casos específicos — **merece confirmação com mais processos antes de virar regra no painel**.

### Valores observados

- R$ 4.900,00 (reforma de cadeiras, PROAD) e R$ 5.000,00 (manutenção de portas de rolo, Almoxarifado) — ambos para o mesmo fornecedor MEI (Josemilson de Araújo Silva).
- Pode haver múltiplas rodadas de renegociação quando o 1º vencedor não tem logística de entrega, ou quando o sistema rejeita automaticamente uma proposta por "valor alterado após expiração da demanda".

### Recomendação

Tratar como rascunho até haver mais processos reais (de unidades e fornecedores diferentes) para confirmar: (1) se o amparo legal é sempre Art. 74 IV, (2) se a ausência total de apensação é sempre assim, (3) se a ordem invertida Requisição-depois-do-Empenho é sistemática ou coincidência de fluxo de trabalho da equipe.

---

## 7. Padrões que atravessam todos os caminhos

- **Templates jurídicos desatualizados são sistemáticos, não pontuais**: Pareceres Técnicos de Dispensa e Inexigibilidade citam a Lei 8.666/93 (revogada) junto com o enquadramento correto na Lei 14.133/2021, na quase totalidade dos casos lidos — não é erro caso a caso, é o modelo de documento em uso. Vale reportar para atualização do template, já que aparece em dezenas de processos.
- **A linguagem "baixa complexidade / módico valor / matriz de risco dispensável"** é fórmula padronizada recorrente em Dispensa e Inexigibilidade — útil para reconhecer o tipo de justificativa esperada, não um sinal de alerta por si só.
- **Painel de Preços (compras.gov.br) é a fonte de validação de preço dominante** em Adesão SRP e frequente em Dispensa/Inexigibilidade — quando um processo novo não cita essa fonte, vale perguntar por quê.
- **Estagnação por meses sem despacho explicando a causa** aparece em todos os caminhos investigados (Pregão, Dispensa, Inexigibilidade, Adesão SRP, Concorrência) — não é exclusivo de nenhum. Candidatos a acompanhamento manual têm um padrão comum: 1 único documento/movimentação recente e nenhum avanço por vários meses.
- **Obras/engenharia é sistematicamente mais lenta e mais imprevisível** que compras "normais", em qualquer caminho que passe por elas (Pregão de obras, Concorrência) — a causa mais comum de atraso longo é espera de dotação orçamentária, não burocracia do ato.
- **Termo de Desapensação é quase sempre correção administrativa pontual** (confirmado empiricamente em Dispensa e Inexigibilidade), mas apareceu também **depois** de contratos concluídos em pelo menos 2 casos de Inexigibilidade — pode ser fechamento de rotina, não só correção de erro; hipótese ainda fraca (poucos casos).
- **A técnica de resolução de id (busca por Tipo=Planejamento com bisecção de janela de datas) funciona bem**, mas tem um ponto cego real: quando o número a resolver é, na verdade, de outro tipo de processo (ex.: tentar resolver um número de Dispensa como se fosse Planejamento/314), a busca simplesmente não encontra nada — não é falha da técnica, é preciso confirmar o tipo certo antes de buscar. Isso aconteceu em parte da amostra de Dispensa/Inexigibilidade quando a direção da apensação foi mal interpretada inicialmente.

---

## 8. Perguntas em aberto — a confirmar com a pessoa antes de tratar como fato

1. **Concorrência — "fase externa invisível"**: em pelo menos 3 dos 13 processos, as movimentações indicam que a licitação já avançou até Contratos-Formalização, mas nenhum documento de Edital/Julgamento/Homologação aparece na área pública do SIPAC. Isso vive só no PNCP? Existe um processo-filho de licitação não capturado? (seção 5)
2. **Contrata+Brasil — amparo legal**: os 2 processos lidos usam Inexigibilidade (Art. 74, IV), não Dispensa (Art. 75) como as fontes públicas genéricas sugeriam. É a regra do programa ou peculiaridade desses 2 casos? (seção 6)
3. **Pregão — abandono da via de pregão em favor de contratação direta**: um processo de material farmacológico mudou de caminho no meio (Pregão → contratação direta) por fracassos recorrentes. Isso é um padrão conhecido/recorrente em outras categorias de material, ou foi pontual desse caso? (seção 1)
4. **Concorrência — apensação de processo embrionário antigo**: a hipótese do CLAUDE.md (14/16 processos apensando planejamento de anos antes) não foi confirmada nem refutada nesta rodada — documentos antigos aparecem embutidos, mas sem Termo de Juntada formal visível. Vale uma rodada dedicada a essa investigação específica?
5. **Adesão SRP e Inexigibilidade — Termo de Desapensação pós-contrato**: apareceu em casos isolados como possível fechamento de rotina (não correção de erro). Vale confirmar com quem opera o SIPAC se isso é prática padrão de arquivamento?
6. **Vários processos "aparentemente estagnados"** foram sinalizados em quase todos os caminhos (listados nas tabelas de cada seção, com número de processo) — vale uma passada humana rápida para confirmar se são mesmo esquecidos ou se há atividade não capturada na área pública.
7. **Discrepância de numeração num item da amostra de Inexigibilidade**: o número indicado como "o processo" na base de trabalho não correspondia ao processo de execução real — pode valer a pena checar se esse tipo de discrepância existe em outras amostragens feitas a partir de `data/processos.json`.

---

*Documento gerado a partir de leitura direta de processos públicos no SIPAC (agosto/2026). Números de processo citados são públicos; nomes de servidores foram omitidos deste documento por não serem necessários para os padrões de análise — os prontuários completos ficam disponíveis nas notas de trabalho de cada lote, caso seja preciso auditar um caso específico com mais detalhe.*
