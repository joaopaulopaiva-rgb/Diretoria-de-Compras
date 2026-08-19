# Base Legal — Caminho Pregão

Documento de apoio jurídico-normativo para o caminho **Pregão** (ver `CLAUDE.md`, seções 3 e 4). Objetivo: reunir, por sub-etapa, a legislação, os decretos, as instruções normativas e a jurisprudência do TCU que fundamentam cada etapa do fluxo — como base para futura geração de minutas de processo e verificações de conformidade. Este é o primeiro caminho, servindo de **piloto de formato** antes de expandir para os outros 5 (Dispensa, Inexigibilidade, Adesão SRP, Concorrência, Contrata+Brasil).

**Não confundir com `ANALISE_PROCESSOS.md`** (que descreve o que foi observado em processos reais da UFRN) nem com `CLAUDE.md` (que descreve a estrutura do painel). Este documento é sobre **a norma em si**: o que a lei/decreto/IN/jurisprudência efetivamente diz, com fonte oficial e data de consulta.

## Como ler cada item

Cada item traz: **o que diz** (resumo fiel, com trecho literal quando relevante) · **fonte** (URL oficial) · **data de consulta** · **status de verificação** (se o texto foi conferido diretamente na fonte oficial nesta sessão, ou se depende de fonte secundária/sessão anterior — sinalizado com transparência).

---

## 1. Lei nº 14.133/2021 (Nova Lei de Licitações e Contratos)

**Fonte oficial**: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm
**Status de verificação**: ⚠️ **planalto.gov.br está bloqueado neste ambiente** (testado via `curl` e via `WebFetch`, em mais de uma ocasião — erro de timeout/CONNECT tunnel failed, sem resposta do servidor). O texto usado aqui vem de um PDF enviado diretamente por você, cujo cabeçalho de cada página confirma a origem (`https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm`, com carimbo de data de acesso "18/08/2026"). Tratamento: fonte oficial genuína, só não acessada *ao vivo* nesta sessão — li a lei na íntegra (Títulos I a V, arts. 1º a 194, incluindo trechos vetados depois promulgados).

### Art. 15 — Consórcios

> "Salvo vedação devidamente justificada no processo licitatório, pessoa jurídica poderá participar de licitação em consórcio, observadas as seguintes normas: [...] responsabilidade solidária dos integrantes pelos atos praticados em consórcio, tanto na fase de licitação quanto na de execução do contrato."

- A regra geral é **permitir** consórcio — a vedação é a exceção, e precisa de **justificativa no processo**.
- Exige: compromisso de constituição subscrito pelos consorciados, indicação de empresa líder, soma de quantitativos (habilitação técnica) e de valores (habilitação econômico-financeira), impedimento de dupla participação, responsabilidade solidária.
- § 1º: acréscimo obrigatório de 10% a 30% na exigência de habilitação econômico-financeira para consórcios (salvo justificativa), não aplicável a consórcios só de ME/EPP (§ 2º).
- **Relevância prática (Pregão/UFRN)**: apesar de a lei favorecer a permissão, editais da UFRN costumam **vedar** consórcio, fundamentando com jurisprudência do TCU (ver seção 5) — a vedação exige motivação própria no processo, a lei por si só não a dispensa.

### Art. 74 — Inexigibilidade (referência cruzada)

Lista as hipóteses de inviabilidade de competição (fornecedor exclusivo, artista consagrado, notória especialização, credenciamento, imóvel com localização/instalação específica). Relevante para o Pregão apenas como **rota alternativa** quando o caminho muda no meio do processo (ver `ANALISE_PROCESSOS.md`, seção 1, "abandono da via de pregão"). Tratamento pleno cabe ao futuro `BASE_LEGAL_INEXIGIBILIDADE.md`.

### Art. 75 — Dispensa (referência cruzada)

Lista as hipóteses de dispensa (valor baixo — inciso I obras/engenharia até R$100 mil, inciso II outras compras/serviços até R$50 mil —, licitação deserta/fracassada do inciso III, e outras hipóteses específicas). Relevante para o Pregão como **rota de saída** quando a licitação fracassa ou o valor pesquisado fica abaixo do limite (mudança Pregão → Dispensa, documentada em `ANALISE_PROCESSOS.md`). Tratamento pleno cabe ao futuro `BASE_LEGAL_DISPENSA.md`.

### Art. 86 — Intenção de Registro de Preços (IRP)

> "O órgão ou entidade gerenciadora deverá, na fase preparatória do processo licitatório, para fins de registro de preços, realizar procedimento público de intenção de registro de preços para, nos termos de regulamento, possibilitar, pelo prazo mínimo de 8 (oito) dias úteis, a participação de outros órgãos ou entidades na respectiva ata e determinar a estimativa total de quantidades da contratação."
>
> § 1º: "O procedimento previsto no caput deste artigo será dispensável quando o órgão ou entidade gerenciadora for o único contratante."

- Regulamentado em detalhe pelo Decreto nº 11.462/2023 (seção 2 abaixo).
- **Confirma diretamente um padrão já observado em processos reais da UFRN** (`ANALISE_PROCESSOS.md`, seção 1): "IRP dispensada por 'órgão único' — quando só a UFRN vai consumir a ata, a DFI justifica formalmente (art. 86 §1º) a não divulgação de IRP". A base legal citada nos processos bate exatamente com o texto oficial.
- §§ 2º a 7º tratam da adesão de não participantes (limite de 50% por órgão, dobro do quantitativo total, regras específicas para adesão a ata federal por estados/municípios) — relevante para o futuro `BASE_LEGAL_ADESAO_SRP.md`, não diretamente para Pregão.

---

## 2. Decreto nº 11.462/2023 (Sistema de Registro de Preços — SRP)

**Fonte oficial**: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11462.htm
**Status de verificação**: ⚠️ Mesma ressalva do item 1 — planalto.gov.br bloqueado neste ambiente; texto usado vem de PDF enviado por você (cabeçalho confirma a mesma origem, carimbo "18/08/2026, 22:43"). Lido na íntegra (12 páginas).

### Art. 3º — Hipóteses de adoção do SRP

> "O SRP poderá ser adotado quando a Administração julgar pertinente, em especial:
> I - quando, pelas características do objeto, houver necessidade de contratações permanentes ou frequentes;
> II - quando for conveniente a aquisição de bens com previsão de entregas parceladas ou contratação de serviços remunerados por unidade de medida, como quantidade de horas de serviço, postos de trabalho ou em regime de tarefa;
> [...]
> V - quando, pela natureza do objeto, não for possível definir previamente o quantitativo a ser demandado pela Administração."

(Inciso III trata de atendimento a mais de um órgão/compras centralizadas; inciso IV trata de compra nacional/execução descentralizada de programa federal — não citados como padrão na amostra da UFRN, mas parte do mesmo artigo.)

- **Confirma diretamente o achado de `ANALISE_PROCESSOS.md`** (seção 1, "Padrões de negociação/precificação"): "Fórmula recorrente de justificativa para SRP: cita incisos I, II ou V do art. 3º" — os três incisos citados nos processos reais são exatamente os que cobrem os cenários mais comuns (contratação recorrente, entrega parcelada, quantitativo imprevisível).

### Art. 9º, §§ 1º e 2º — Dispensa da IRP

> "Art. 9º [...] realizar procedimento público de IRP para possibilitar, pelo prazo mínimo de oito dias úteis, a participação de outros órgãos [...]
> § 1º O prazo previsto no caput será contado do primeiro dia útil subsequente à data de divulgação da IRP no SRP digital e no Portal Nacional de Contratações Públicas - PNCP [...]
> § 2º O procedimento previsto no caput poderá ser dispensado quando o órgão ou a entidade gerenciadora for o único contratante."

- Este é o dispositivo regulamentador que **operacionaliza** o art. 86, §1º da Lei 14.133/2021 (item 1 acima) — os dois juntos formam a base legal completa da dispensa de IRP por "órgão único", usada de forma recorrente pela DFI da UFRN.

---

## 3. Instrução Normativa SGD/ME nº 94/2022 (Contratações de TIC)

**Fonte oficial**: https://www.gov.br/governodigital/pt-br/contratacoes-de-tic/legislacao/processo-de-contratacao-de-solucoes-de-tic-regido-pela-lei-ndeg-14-133-de-2021
**Status de verificação**: ✅ **Acessado ao vivo nesta sessão** via WebFetch (18/08/2026 → 19/08/2026, sessão contínua) — gov.br está liberado neste ambiente, diferente de planalto.gov.br/TCU. Confirmação adicional: os artigos citados abaixo batem com o conteúdo dos modelos de TR de TIC da AGU (lidos na íntegra, ver seção 6).

Disciplina o planejamento, seleção do fornecedor e gestão de contratos de soluções de Tecnologia da Informação e Comunicação, regida pela Lei 14.133/2021. Aplica-se a pregões cujo objeto seja caracterizado como solução de TIC — variante identificada em `ANALISE_PROCESSOS.md` (seção 1) como "consistentemente mais lenta" dentro do caminho Pregão.

- **Art. 19, III** — fixa a obrigatoriedade de o instrumento contratual prever "valores e procedimentos para retenção ou glosa no pagamento [...] que só deverá ocorrer quando a contratada não atingir os valores mínimos aceitáveis fixados nos critérios de aceitação" — base do indicador IAE (compras) / IAP (serviços) usado nos modelos de TR de TIC da AGU.
- **Art. 31** — institui a **Reunião Inicial**, obrigatória no início da execução contratual, com pauta mínima definida (apresentação de preposto, esclarecimento de rotinas de fiscalização, entrega de documentos, etc.).
- **Art. 33, incisos I, II, IV** — define os papéis de fiscalização do contrato: Gestor do Contrato, Fiscal Técnico e Fiscal Administrativo, cada um com atribuições próprias.
- **Etapa extra no planejamento**: exige Despacho de Instituição de Equipe de Planejamento da Contratação (Integrante Requisitante + Integrante Técnico + Integrante Administrativo + Autoridade Máxima da Área de TIC) — não existe no fluxo padrão de Pregão sem TIC. Esse achado normativo **explica estruturalmente** por que `ANALISE_PROCESSOS.md` observa TIC como "consistentemente mais lento".
- **Não coberto pelo Parecer Referencial nº 00006/2025** (ver seção 4) — contratações de TIC estão expressamente excluídas do rito de dispensa de exame jurídico individualizado, exigindo parecer jurídico próprio mesmo em valores baixos.

---

## 4. Parecer Referencial nº 00006/2025/GERTEC/ELIC/PGF/AGU — Dispensa de exame jurídico individualizado

**Fonte**: modelo obtido diretamente do site da AGU (Equipe de Licitações e Contratos — ELIC), lido na íntegra em PDF.
**Identificação**: NUP 00407.059564/2025-42 · Fonte de publicação: SAPIENS/SUPERSAPIENS (https://supersapiens.agu.gov.br/apps/processo/54790547/visualizar/latest) — sistema de acesso restrito da AGU; o PDF obtido via gov.br/agu é a via de acesso público ao conteúdo do parecer.
**Status de verificação**: ✅ Lido na íntegra nesta sessão.

### O que diz, com precisão (inclui exceções importantes)

> "Esta Manifestação Jurídica Referencial se aplica aos procedimentos licitatórios para aquisição de bens comuns, na modalidade pregão eletrônico, processados ou não pelo Sistema de Registro de Preços, com critério de julgamento pelo menor preço e valor estimado da contratação igual ou inferior a R$ 1.000.000,00 (um milhão de reais)."

**Fundamento**: Orientação Normativa AGU nº 55/2014 + Portaria PGF nº 262/2017 — dispensam análise jurídica individualizada para matérias jurídicas idênticas e recorrentes, desde que a área técnica ateste expressamente o enquadramento.

**⚠️ Exceções expressas — NÃO se aplica a**:
- a) aquisição de **gêneros alimentícios** (há parecer referencial próprio — nº 00008/2025, também lido nesta sessão);
- b) aquisição de bens caracterizados como **solução de TIC**;
- c) **gás liquefeito de petróleo** (GLP);
- d) bens com **serviços agregados** licitados como itens separados;
- e) **aquisição internacional**.

**Condições para uso**: o ente assessorado deve atestar expressamente o enquadramento (art. 3º, § 2º, Portaria PGF/AGU nº 262/2017), usar os modelos atualizados da AGU (TR, edital, contrato, ata de SRP, lista de verificação) e observar o Instrumento de Padronização dos Procedimentos de Contratação (IPP).

- **Confirma diretamente** o achado de `ANALISE_PROCESSOS.md` (seção 1): "Jurídico — via Parecer Referencial AGU (valor < R$1M): mesmo dia — atalho recorrente para objetos padronizados de menor valor" — e explica por que TIC (excluído do parecer) segue pelo rito de análise individualizada mais lenta (14-18 dias, mesma seção).

---

## 5. Acórdãos do TCU — Vedação de participação de consórcio

**Fonte oficial**: portal.tcu.gov.br / pesquisa.apps.tcu.gov.br
**Status de verificação**: 🔴 **Não verificado em fonte oficial nesta sessão.** Ambos os domínios do TCU estão bloqueados neste ambiente — testado por `curl` e por `WebFetch`, em mais de uma ocasião ao longo da sessão (erro `EGRESS_BLOCKED` explícito do proxy de rede, e timeout de conexão). Não há upload de PDF do usuário para esses acórdãos.

**O que se sabe, com transparência sobre a origem**:
- Acórdãos **2633/2019**, **1.946/2016** e **1316/2010** — citados como fundamento padrão de vedação de participação de consórcio em editais reais da UFRN, segundo `ANALISE_PROCESSOS.md` (seção 1): *"praticamente todo Edital cita os mesmos três acórdãos TCU [...] texto padronizado copiado entre processos"*.
- O modelo de edital-padrão da AGU (lido na íntegra nesta sessão) **não cita esses acórdãos por número** — trata a vedação de consórcio como opção parametrizável no edital, sem fundamentação jurisprudencial embutida no modelo. Ou seja, a citação desses três acórdãos é **prática local da UFRN**, adicionada por fora do modelo-padrão da AGU — não uma exigência normativa nacional uniforme.
- **Conteúdo esperado** (não confirmado em texto oficial): jurisprudência do TCU historicamente trata a vedação de consórcio como exceção que exige motivação técnica no processo (risco à competitividade, natureza do objeto), alinhada ao art. 15 da Lei 14.133/2021 (vedação "devidamente justificada").

**Recomendação**: antes de usar esses três acórdãos como fundamento em uma minuta gerada, valeria confirmar o texto integral — seja por upload seu de PDF/print, seja tentando novamente o acesso ao TCU em outro momento (pode ser bloqueio temporário do ambiente, não necessariamente permanente).

## 6. Acórdão TCU 2273/2024 — ETP não é anexo obrigatório do edital

**Fonte oficial**: portal.tcu.gov.br / pesquisa.apps.tcu.gov.br
**Status de verificação**: 🔴 **Não verificado em fonte oficial nesta sessão** (mesmo bloqueio da seção 5). Segundo contexto de sessão anterior a este trabalho, este acórdão teria sido confirmado como: Plenário, relator Min. Benjamin Zymler, julgado em 23/10/2024, entendendo que o Estudo Técnico Preliminar (ETP) não precisa necessariamente compor o edital como anexo formal. **Esse dado não pôde ser reconfirmado com leitura direta da fonte nesta sessão** — está registrado aqui como já reportado antes, não como verificado agora. Tratar com cautela até confirmação direta (upload de PDF/print do acórdão, se disponível).

---

## 7. Modelos e pareceres da AGU consultados (apoio, não fonte primária de lei)

Para contexto de como a base legal acima se traduz em documento real, foram lidos na íntegra os seguintes modelos oficiais da AGU (gov.br/compras — Modelos de Licitações e Contratos) relevantes ao caminho Pregão:

- Edital de Pregão/Concorrência (padrão e variante TIC)
- Ata de Registro de Preços
- Termo de Referência — Compras (padrão e variante TIC)
- Termo de Referência — Serviços/Obras (padrão e variante TIC)
- Contrato — Compras/Serviços TIC
- 6 Listas de Verificação (Compras/Serviços, Serviços com Mão de Obra, Engenharia, Adesão a ARP, Aditivos, TIC)
- Os 10 Pareceres Referenciais da ELIC/PGF/AGU disponíveis (nºs 00001 a 00009/2025 e 00001/2026), cobrindo: prorrogação contratual (Lei 14.133 e Lei 8.666), inexigibilidade para água/esgoto, energia elétrica, prorrogação de ARP, aquisições ≤R$1M (detalhado na seção 4), aditivo de supressão, gêneros alimentícios, adesão a ARP, jornada de trabalho.

Esses documentos não são "lei", mas são a tradução prática da base legal em minuta — úteis para gerar documentos consistentes com o que a própria AGU orienta.

---

## Resumo do que falta verificar (transparência)

| Item | Situação |
|---|---|
| Lei 14.133/2021 (arts. 15, 74, 75, 86) | ✅ Lida na íntegra, via PDF fornecido por você (fonte genuína, não acessada ao vivo) |
| Decreto 11.462/2023 (art. 3º, art. 9º) | ✅ Lido na íntegra, via PDF fornecido por você (fonte genuína, não acessada ao vivo) |
| IN SGD/ME 94/2022 | ✅ Acessada ao vivo nesta sessão (gov.br liberado) |
| Parecer Referencial 00006/2025 AGU | ✅ Lido na íntegra nesta sessão |
| Acórdãos TCU 2633/2019, 1.946/2016, 1316/2010 | 🔴 Bloqueado — só referência indireta via `ANALISE_PROCESSOS.md` |
| Acórdão TCU 2273/2024 | 🔴 Bloqueado — só referência indireta de sessão anterior, não reconfirmada |

---

*Documento piloto — caminho Pregão. Formato a validar com você antes de replicar para Dispensa, Inexigibilidade, Adesão SRP, Concorrência e Contrata+Brasil.*
