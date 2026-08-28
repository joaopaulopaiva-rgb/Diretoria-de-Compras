# Painel de Acompanhamento de Compras — UFRN

Contexto persistente do projeto. Qualquer sessão do Claude Code que trabalhe neste repositório deve ler este arquivo primeiro — ele substitui a necessidade de colar um resumo de contexto manualmente a cada conversa.

## 1. O que é este projeto

Sistema de acompanhamento visual dos processos de compras públicas da UFRN (pregões eletrônicos), que tramitam por várias unidades: **DPGC** (Divisão de Planejamento e Gerenciamento de Compras), **DFI** (Divisão de Fase Interna de Compras), **Jurídico** (Procuradoria Federal) e **DFE** (Divisão de Fase Externa de Compras).

Existe um protótipo funcional em HTML (construído em conversas anteriores, fora deste repositório ainda) com cards visuais, filtros, alertas de prazo e métricas — ele é o ponto de partida visual, não algo a descartar. O objetivo atual é: (1) automatizar a coleta de dados que hoje é manual, e (2) redesenhar a experiência visual, que a pessoa quer mais "disruptiva" que um Kanban tradicional — ainda em fase de tentativa e erro, sem direção visual fechada.

Fonte de dados: **SIPAC** (sistema da UFRN), área pública, sem necessidade de login: `https://sipac.ufrn.br/public/jsp/processos/processo_detalhado.jsf?id=NÚMERO`.

## 2. Regra estrutural: Planejamento vs. Pregão são processos diferentes

- Todo processo de compra **nasce como processo de planejamento** (tipo 33.00, "PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO") na DPGC, com número próprio.
- Quando a DPGC termina, o processo vai à DFI, que **formaliza um processo de pregão novo, com número próprio**; o processo de planejamento vira o **apenso/acessório**.
- **DFD, ETP, TR e Lista de Verificação são sempre lidos no processo de PLANEJAMENTO.** Análise DFI, Pesquisa de Preços, IRP, Elaboração de Edital, Jurídico e DFE são sempre lidos no **processo de PREGÃO**. Nunca misturar a fonte — mesmo que o mesmo tipo de documento apareça copiado como anexo no processo "errado" (já observado na prática), o dado que conta é sempre o da fonte certa.
- Fluxo fora do padrão (nomes diferentes, sem pregão vinculado, etc.) é **exceção rara**. Quando acontecer, sinalizar e perguntar à pessoa antes de presumir — não tentar adivinhar.
- Já houve um caso de apensação tecnicamente incorreta no próprio SIPAC (processo 23077.055744/2025-30). Sempre que a lógica de datas/movimentações parecer inconsistente, perguntar antes de assumir.

## 3. Sub-etapas e documentos-gatilho (marcos) — Pregão

| # | Sub-etapa | Processo-fonte | Documento/evento de início | Documento/evento de fim |
|---|---|---|---|---|
| 1 | DFD | Planejamento | Data de cadastro do processo | Despacho de Autorização da Formalização de Demanda |
| 2 | ETP | Planejamento | ETP Digital | Despacho de Autorização dos Estudos Técnicos |
| 3 | TR | Planejamento | TR Digital | Despacho de Autorização do Termo de Referência |
| 4 | Lista de Verificação | Planejamento | Despacho de Autorização do TR (mesmo doc que fecha TR) | Envio da DPGC para a DFI (movimentação) |
| 5 | Análise DFI | Pregão | Envio da DPGC para a DFI (mesmo marco, registrado no pregão) | Nota Informativa Fase Interna — Pesquisa de Preços |
| 6 | Pesquisa de Preços | Pregão | Nota Informativa — Pesquisa de Preços | Nota Informativa — Intenção de Registro de Preços |
| 7 | IRP | Pregão | Nota Informativa — IRP (mesmo doc que fecha a anterior) | Nota Informativa — Elaboração de Edital |
| 8 | Elaboração de Edital | Pregão | Nota Informativa — Elaboração de Edital | Certificação Processual |
| 9 | Jurídico | Pregão | Certificação Processual (mesmo doc que fecha a anterior) | Análise de Parecer Jurídico |
| 10 | DFE | Pregão | Divulgação da Licitação / Publicação no D.O. | Homologação |

**Extração de data dos marcos:** usar a data mostrada na própria tabela de documentos da página pública do processo — **não abrir o PDF** para checar a data de assinatura interna (decisão explícita: o custo de baixar/ler cada documento não compensa; a data da tabela já é próxima o suficiente da data de assinatura real).

## 4. Outros caminhos de contratação (além do Pregão)

Todo processo de compra nasce como Planejamento (33.00, seção 2), mas nem todo planejamento vira Pregão. Outros caminhos possíveis: **Dispensa de Licitação**, **Inexigibilidade de Licitação**, **Adesão a Ata de Registro de Preços (SRP)**, **Concorrência** e **Contrata+Brasil**. O caminho pode ser definido já no início do planejamento, e pode **mudar no meio do processo** (ex.: Pregão → Dispensa, quando a pesquisa de preços indica valor abaixo do limite de dispensa).

Mapeamento confirmado por auditoria empírica no SIPAC (agosto/2026, ~20 processos por tipo, lidos por completo, incluindo abertura de todo Termo de Juntada por Apensação e do processo apensado citado nele). **Ponto crítico de método:** pular a leitura do Termo de Juntada e do processo apensado leva a conclusões erradas — isso já aconteceu numa primeira rodada de pesquisa, que concluiu (errado) que esses caminhos não apensavam planejamento real.

**Diferença estrutural chave em relação ao Pregão:** no Pregão, o planejamento concluído "vira" um processo de pregão novo (número novo, seção 2). Nos outros caminhos — exceto Concorrência — o planejamento concluído é **apensado** a um processo de execução que **já existe**, aberto por outra unidade (tipicamente a DFI).

### 4.1 Dispensa de Licitação

Tipo de Processo no SIPAC: value `150`.

| # | Sub-etapa | Processo-fonte | Documento/evento de início | Documento/evento de fim |
|---|---|---|---|---|
| 1 | DFD | Planejamento (apensado, DPGC) | Ofício da unidade requisitante | Documento de Formalização da Demanda Digital (DFD Digital) |
| 2 | ETP | Planejamento (apensado, DPGC) | Estudo Técnico Preliminar Digital (ETP Digital) | Mapa de Gerenciamento de Riscos Digital |
| 3 | TR | Planejamento (apensado, DPGC) | Termo de Referência Digital (TR Digital) | — |
| 4 | Autorização da Contratação Direta | Planejamento (apensado, DPGC) | Pesquisa de preço / Requisição de Materiais | Autorização de Formalização - Contratação Direta |
| 5 | Apensação | Dispensa (DFI) | Recebimento do planejamento na DFI | Termo de Juntada por Apensação |
| 6 | Julgamento/Comparação de Preços | Dispensa (DFI) | Relatório Detalhado de Requisições do Processo | Quadro Comparativo de Propostas / Parecer Técnico |
| 7 | Divulgação (só casos maiores) | Dispensa (DFE) | Aviso de Dispensa Eletrônica | Divulgação da Dispensa de Licitação |
| 8 | Disponibilidade Orçamentária | Dispensa (PROAD/Orçamento) | Encaminhamento PROAD → Orçamento | Declaração de Disponibilidade Orçamentária |
| 9 | Empenho | Dispensa (DCF) | Encaminhamento COMPRAS/PROAD → DCF | Nota de Empenho |

- **Padrão dominante** (15/18 apensados confirmados na amostra): planejamento apensado real, com a sequência completa acima.
- **Variante minoritária** (2/20 amostras): DFD/ETP acontecem dentro do próprio número do processo de Dispensa, sem Termo de Juntada — a Dispensa acumula o papel de planejamento + execução.
- Jurídico é raro (1/20) — não é regra.
- **Fecha com Nota de Empenho**, não com Homologação (coerente com contratação direta, Lei 14.133/2021).

### 4.2 Inexigibilidade de Licitação

Tipo de Processo no SIPAC: value `74`.

Estrutura idêntica à de Dispensa (tabela da seção 4.1), com uma diferença: na etapa de ETP aparece também a **Carta de Exclusividade** (justificativa de fornecedor exclusivo). Fecha com **Nota de Empenho** via Nota de Resumo para Empenhos.

- 100% dos processos amostrados têm Termo de Juntada por Apensação — taxa de apensação ainda maior que Dispensa.
- Sem Jurídico, sem DFE.
- **Ruído a filtrar:** `Termo de Desapensação` (visto em ~3/20) é uma correção administrativa pontual (ex.: "retirado para correção do documento"), não uma etapa estrutural — não usar como sinal de mudança de status.

### 4.3 Adesão a Ata de Registro de Preços (SRP)

Tipo de Processo no SIPAC: value `258`. É o padrão mais limpo e consistente de todos os caminhos investigados (19/19 apensados confirmados como Planejamento real; 18/18 abertos por completo confirmam a sequência abaixo).

| # | Sub-etapa | Processo-fonte | Documento/evento de início | Documento/evento de fim |
|---|---|---|---|---|
| 1 | DFD | Planejamento (apensado, DPGC) | Ofício da unidade requisitante | Documento de Formalização da Demanda Digital (DFD Digital) |
| 2 | ETP + Verificação | Planejamento (apensado, DPGC) | Estudo Técnico Preliminar Digital (ETP Digital) | SICAF + Consulta Consolidada de Pessoa Jurídica — TCU |
| 3 | Autorização de Formalização | Planejamento (apensado, DPGC) | Pesquisa de preço (validação da ata) | Autorização de Formalização - Adesão a Ata de Registro de Preços |
| 4 | Autorização de Adesão (fechamento) | Planejamento (apensado, DFI) | Documento Comprobatório de Licitação | **Autorização de Adesão a Ata de Registro de Preços** |
| 5 | Apensação / Registro | Adesão SRP (DFI, invólucro tipo=258) | Recebimento do planejamento já concluído | Termo de Juntada por Apensação |

- O documento de fechamento real (`Autorização de Adesão a Ata de Registro de Preços`) vive **dentro do processo de Planejamento apensado**, não no processo tipo=258 — esse é só um invólucro administrativo curto que recebe o planejamento já quase pronto (a apensação costuma acontecer no mesmo dia ou 1 dia depois da Autorização de Adesão).
- Sem pesquisa de preço própria, sem Jurídico, sem DFE — a pesquisa já foi feita pelo órgão gerenciador da ata.
- Depois da Adesão: dependendo do objeto, pode seguir para Contrato formal (não só empenho direto).
- **Execução (fora do escopo de acompanhamento por ora):** cada unidade requisitante pede via processos próprios de `Solicitação de Material em Registro de Preço` (tipo `632`) — volume alto (400+ históricos), não investigado a fundo.

### 4.4 Concorrência

Tipo de Processo no SIPAC: value `220`. **Atenção ao ruído:** ~58% dos resultados de busca por esse tipo são processos acessórios de gestão contratual pós-homologação (reequilíbrio, aditivo, reajuste, fiscalização) classificados sob o mesmo tipo — filtrar por "Assunto Detalhado" antes de tratar um resultado como licitação original. Só existem **16 processos de Concorrência originais** em todo o período 2025-2026 (modalidade rara, concentrada em obras/engenharia).

| # | Sub-etapa | Processo-fonte | Documento/evento de início | Documento/evento de fim |
|---|---|---|---|---|
| 0 | *(hipótese, não confirmada)* Planejamento anterior | Processo apensado mais antigo (CAOSE/INFRA) | Formalização da Demanda | DFD Digital de versão anterior do projeto |
| 1 | DFD | Concorrência (CAOSE/INFRA) | Documento de Formalização da Demanda Digital (DFD Digital) | Despacho de Autorização da Formalização de Demanda |
| 2 | ETP | Concorrência (CAOSE/INFRA) | Estudo Técnico Preliminar Digital (ETP Digital) | Despacho de Autorização dos Estudos Técnicos |
| 3 | TR + Projetos de Engenharia | Concorrência (CAOSE/INFRA → DP/INFRA) | Termo de Referência Digital + projetos executivos/ART/orçamentos/BDI | Despacho de Autorização do Termo de Referência |
| 4 | Elaboração de Edital e Certificação | Concorrência (CAOSE/INFRA → PROAD) | Minuta de Instrumento Jurídico | Lista de Verificação + Certificação Processual |
| 5 | Jurídico | Concorrência (SPF) | Encaminhamento PROAD → SPF | Parecer Jurídico |
| 6 | DFE (Fase Externa) | Concorrência (DFE, passagem breve por DFI) | Divulgação da Licitação | Propostas, habilitação, pareceres técnico/contábil |
| 7 | Julgamento e Homologação | Concorrência (DFE) | Termo de Julgamento | Homologação |

- **Diferente dos demais caminhos:** DFD/ETP/TR ficam **dentro do próprio processo** de Concorrência, tramitado pela **CAOSE/INFRA** (não pela DPGC) — não há apensação de planejamento separado para essa parte.
- **Hipótese não confirmada (etapa 0):** 14/16 processos também têm um Termo de Juntada apensando um processo bem mais antigo (2021-2025) — possivelmente um planejamento embrionário/anterior de um projeto de obra que mudou de escopo ao longo dos anos. Só 1 caso foi aberto e lido por completo até hoje. Tratar como hipótese em investigação, não como fato — é por isso que a trilha visual mostra esse nó de forma tênue/não confirmada.
- **Homologação acontece de fato** (12/16 = 75% dos processos originais já chegaram lá) — segue o mesmo padrão de fechamento do Pregão (Termo de Julgamento + Homologação, ambos DFE).
- Pós-homologação, o processo segue em `Contratos/PROAD` (aditivos, reajustes, fiscalização) — fora do escopo de acompanhamento ativo, mesmo tratamento dado ao Homologado do Pregão (seção 7).

### 4.5 Contrata+Brasil (rascunho — baseado em fontes públicas, ainda não confirmado com processos reais da UFRN)

Programa federal recente (lançado em 2025), com plataforma própria, voltado a MEI/microempresas — dispensa eletrônica simplificada com base no art. 75 da Lei 14.133/2021. **Não foi auditado no SIPAC ainda** (a pessoa responsável já abriu alguns processos reais, mas o fluxo interno ainda não está fechado) — o que segue é conhecimento genérico de fontes públicas, não uma tabela de marcos confirmada como as anteriores.

- Dispensa ETP, Termo de Referência e edital — essas etapas já vêm prontas/padronizadas do governo federal, o órgão só publica a demanda.
- Fluxo genérico conhecido: publicação da demanda pelo órgão → notificação automática a MEIs cadastrados (via WhatsApp) → envio de propostas pelos fornecedores → seleção do prestador pelo órgão → formalização (Nota de Empenho ou Contrato via Sistema Contratos Gov.br).
- Cadastro do fornecedor é simplificado (só CNPJ, que alimenta o SICAF automaticamente).
- **Não presumir** como isso aparece no SIPAC da UFRN (nome do tipo de processo, se apensa planejamento como os demais caminhos ou se roda inteiramente dentro de um processo só) até validação com processos reais — sinalizar e perguntar à pessoa antes de tratar qualquer achado como confirmado.

### 4.6 Padrões que atravessam todos os caminhos

- Apensar um Planejamento (33.00) real e completo é o **padrão dominante** em Dispensa, Inexigibilidade e Adesão SRP — não a exceção.
- A busca pública por Tipo de Processo vem poluída, em **todos** os tipos (não só Concorrência), por processos acessórios de gestão contratual pós-award (reequilíbrio, aditivo, redução de jornada, fiscalização) — sempre checar o "Assunto Detalhado" antes de tratar um resultado como uma contratação original.
- A busca pública direta por número de processo continua **não funcionando** via automação (mesmo testada de novo com número válido conhecido — ver seção 12). Para resolver "número de processo apensado → id do processo", a técnica viável é montar um índice de processos por Tipo de Processo (`314` = Planejamento) cobrindo o período provável e cruzar os números — funciona, mas exige janelas de busca estreitas o suficiente para não truncar (~15 resultados por consulta).
- Existe uma segunda via de busca pública, por **Tipo de Documento** (`documentosForm`, aba `p-buscadocumentos`, campo `tipo_consulta_documento=500`) — útil quando não se sabe o Tipo de Processo do processo-alvo (ex.: localizar direto todo documento "Autorização de Adesão a Ata de Registro de Preços" por período e achar seu "Processo Associado").

## 5. Fases macro e trilha visual

Ordem: **Planejamento (DPGC) → Fase Interna (DFI) → Jurídico (Projur/Análise) → Fase Externa (DFE) → Homologado**.

Único estado terminal considerado: **Homologado**. Processos cancelados/revogados são exceção rara e não recebem tratamento especial por ora. Licitações fracassadas/desertas seguem para nova tentativa até serem homologadas — não saem do fluxo.

Essa é a trilha do caminho Pregão. Os demais caminhos (seção 4) têm suas próprias trilhas — ver seção 4 para as sequências de cada um.

## 6. Cores e alertas — prática interna (não é exigência legal)

| Categoria | Amarelo a partir de | Vermelho a partir de |
|---|---|---|
| Aguardando PROAD | 2 dias | 3 dias |
| Aguardando Procuradoria/Jurídico | 10 dias | 20 dias |
| Em elaboração ativa (DPGC/DFI) | 5 dias | 10 dias |
| Circulando em unidades técnicas/requisitantes | 5 dias | 10 dias |

Esses limites são práticos, definidos pela equipe (não normativos) — ajustáveis livremente no sistema.

**Urgente:** sempre manual. Nunca inferir automaticamente — só quando a pessoa sinalizar explicitamente.

## 7. Gestor (responsável)

O gestor só é exibido/rastreado **enquanto o processo está na DPGC**. Ao sair da DPGC (entrar na DFI), o campo de gestor deixa de ser mostrado — outros servidores assumem e isso não precisa de acompanhamento no painel por ora.

Gestores confirmados: Jorge Henrique Teotonio de Lima Melo, Adrielly Cristiane Silva Vital Nunes, Lucas, Pedro (confirmar se é o mesmo "Pedro da Rocha Souza" que aparece em documentos), Chianc Leocadio de Lima, Flavio Carlos de Albuquerque, Thays Lins Galvao de Albuquerque Bastos. Renato Luiz Vieira de Carvalho não trabalha mais na equipe — processos dele são reatribuídos a Jorge.

## 8. Estados especiais — detecção automática

- **Homologado:** documento tipo "HOMOLOGAÇÃO" saindo da DFE para a Diretoria de Compras → marcar fase Homologado automaticamente, e excluir das contagens de acompanhamento ativo (só aparece numa aba própria de histórico).
- **Em recurso:** documentos "RECURSO ADMINISTRATIVO DE LICITAÇÃO" + "JULGAMENTO DE RECURSO" → marcar `emRecurso: true` automaticamente, fase continua DFE.
- **Suspenso:** sempre um evento da **DFE**. Regra de detecção: toda movimentação **DFE → Diretoria de Compras** que não seja homologação nem recurso (pelos critérios acima) obriga o sistema a abrir o documento de envio dessa movimentação e ler o texto — se confirmar suspensão, marcar `suspenso: true` automaticamente. Fora desse cenário específico, nunca precisa abrir documento só para checar suspensão.

## 9. Geração do resumo de situação atual

Para cada processo, pegar no máximo os **2 documentos mais recentes** (da página mais avançada — pregão se existir, senão planejamento) + as movimentações recentes, ler o conteúdo e gerar um resumo curto em texto livre (estilo do campo "situação atual" já usado no protótipo). Não ler mais que isso — decisão explícita para não pesar o processo.

## 10. Casos de baixa confiança

Se um despacho estiver com "Acesso Negado", data ambígua, ou qualquer inconsistência de apensação: **não presumir, não registrar** — sinalizar diretamente no chat com a pessoa e perguntar. **Não** poluir o dashboard/cards com indicadores de "precisa verificar" — isso fica de fora da interface visual.

## 11. Descoberta automática de processos novos

Pipeline (roda toda sexta-feira automaticamente, e sob demanda quando a pessoa pedir):

1. Buscar no portal público (`https://sipac.ufrn.br/public/jsp/portal.jsf`, aba "Processos") por **Tipo de Processo = PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO (33.00)** (option value `314`) **+ Período de Cadastro = hoje até 7 dias atrás**.
2. Percorrer **todas as páginas** de resultado (há paginação real — testado com 23 registros em 2 páginas).
3. Descartar processos cujo número/id já estejam registrados como "já vistos" (arquivo local de cache) — evita reabrir/reanalisar processo repetido.
4. Para cada processo novo: abrir a página pública e checar o **primeiro documento** da lista. Se for **"DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA DIGITAL (DFD DIGITAL)"**, é um processo válido para acompanhar — adicionar ao painel e rodar a extração de marcos (seção 3). Se não for, marcar como "visto, fora do padrão" e não tratar mais.

Além da descoberta semanal, dois outros processos automáticos mantêm o painel em dia (**desde 28/08/2026 nenhum dos dois roda mais em horário fixo** — ambos disparam quando a pessoa clica em "Entrar no painel" no portão, o que ela faz sempre que abre o site; ver `.github/workflows/portao_atualizar.yml`):

- **Atualização geral de marcos** (`scripts/atualizar_marcos.py`): repuxa os documentos/movimentações de cada processo já rastreado e recalcula fase/sub-etapa (seção 3).
- **Revisar processos ignorados** (`scripts/revisar_ignorados.py`): para cada processo em `data/ignorados.json` (marcado "Ignorar" no portão em algum momento), compara a data do último documento hoje com a que estava registrada no momento em que foi ignorado. Se mudou (voltou a se movimentar), devolve automaticamente à fila do portão (`data/portao_pendentes.json`) com uma nota explicando o motivo. Se não mudou, continua ignorado, sem gerar alerta.

Os dois workflows antigos (`atualizar_marcos.yml` em cron diário, e a revisão de ignorados dentro de `descoberta_semanal.yml`) continuam existindo só como `workflow_dispatch` (rodar manualmente na aba Actions do GitHub), sem agendamento — mantidos como saída de emergência caso a pessoa passe muito tempo sem abrir o painel.

## 12. Limitações técnicas conhecidas do SIPAC público

- A busca pública **por número de processo/documento** (formulário "N° Processo"/"N° Documento") **não funciona via automação simples** (POST direto) — parece depender de estado de sessão JSF que não se reproduz fora de um navegador real. **Não insistir nesse caminho** (testado de novo em agosto/2026, inclusive com número de processo válido conhecido — confirma a limitação).
- A busca pública **por tipo de processo/documento** (dropdown) **funciona bem via automação** — é o caminho usado para descoberta (seção 11) e também para achar processos por tipo de documento (ex.: todos os despachos de um tipo, cada um informando "Processo Associado: NNNNN" no rodapé).
- A **paginação de resultados também é pouco confiável via POST** — o seletor de página tende a sempre retornar a página 1 independente do valor submetido; o contorno é estreitar a janela de datas (mês/quinzena) até o "N Registro(s) Encontrado(s)" caber inteiro numa página (~15 resultados por consulta).
- Links "Visualizar Documento" na listagem de documentos são `href="#"` com JavaScript (`onclick`), mas o `onclick` contém uma URL pública real de download (`/public/verArquivoDocumento?idArquivo=...&key=...`) que funciona sem login — já validado baixando e lendo PDFs reais de processos de planejamento e de pregão, de vários tipos de documento. Alguns documentos (ex. Termo de Juntada por Apensação) renderizam direto como HTML via `documento_visualizacao.jsf?idDoc=...` — mais rápido de ler, tentar primeiro quando aplicável.
- A conexão com o SIPAC é instável (erros de "connection reset" frequentes, tanto em `curl` quanto em navegador automatizado) — qualquer automação precisa de lógica de nova tentativa (retry), tipicamente resolve em 2-4 tentativas.
- Navegador automatizado (Playwright/Chromium) teve problemas consistentes de conexão neste ambiente específico — `curl` com retry é o caminho confiável hoje.
- Não é possível abrir o processo só com o número (sem o `id=` interno) exceto pelos caminhos de busca por tipo (seção 11) — a busca direta por número não funciona.

## 13. Acesso e edição

Por enquanto: todo mundo (quando o painel for compartilhado) pode **ver** tudo. Só a pessoa dona do projeto pode **editar/adicionar** processos. Não construir controle de permissão granular por unidade agora.

## 14. Estilo de trabalho combinado

- Fazer perguntas de esclarecimento **antes** de implementar mudanças ambíguas.
- Nunca presumir vínculos entre processos (planejamento ↔ pregão, ou planejamento ↔ execução nos demais caminhos) sem confirmação.
- Ao processar em lote, perguntar se deve narrar o progresso ou trabalhar silenciosamente e reportar o resultado consolidado.
- Testar empiricamente antes de afirmar uma capacidade técnica (ex.: baixar e ler um documento de verdade antes de dizer que "funciona") — várias suposições iniciais deste projeto (links de documento "mortos", busca por número, etc.) se mostraram erradas só depois de testar de fato.
- **Nunca pular a leitura de documentos-chave (ex. Termo de Juntada por Apensação) por economia** quando a pergunta é justamente sobre a estrutura do fluxo — uma rodada de pesquisa que pulou essa leitura chegou a conclusões erradas sobre os caminhos da seção 4, corrigidas só numa segunda rodada mais profunda.
- Antes de lançar uma tarefa de pesquisa longa e autônoma, verificar rapidamente ao vivo (poucos exemplos, foreground) e reportar à pessoa antes de comprometer o tempo numa tarefa longa em background — dá chance dela corrigir o rumo com detalhes que só ela sabe.

## 15. Em aberto (ainda não decidido)

- Design visual do dashboard: a pessoa quer algo mais "disruptivo" que um Kanban/Trello tradicional, mas ainda não sabe exatamente o quê — vai ser por tentativa e erro.
- Arquitetura de implementação (onde/como persistir os dados dos processos, tecnologia do frontend) — ainda não definida.
- Mecanismo exato de agendamento da atualização semanal automática (ex.: rotina agendada) — a capacidade existe, falta desenhar a implementação.
- Contrata+Brasil (seção 4.5) ainda precisa de auditoria real no SIPAC para confirmar a tabela de marcos, como já foi feito com os demais caminhos.
- Mecânica exata de troca de caminho no meio do processo (ex.: Pregão → Dispensa) — se gera número de processo novo ou mantém o mesmo, e como isso deve ficar registrado no histórico (`caminhoHistorico`) do sistema — ainda não definido.
