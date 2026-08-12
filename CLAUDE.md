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

## 3. Sub-etapas e documentos-gatilho (marcos)

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

## 4. Fases macro e trilha visual

Ordem: **Planejamento (DPGC) → Fase Interna (DFI) → Jurídico (Projur/Análise) → Fase Externa (DFE) → Homologado**.

Único estado terminal considerado: **Homologado**. Processos cancelados/revogados são exceção rara e não recebem tratamento especial por ora. Licitações fracassadas/desertas seguem para nova tentativa até serem homologadas — não saem do fluxo.

## 5. Cores e alertas — prática interna (não é exigência legal)

| Categoria | Amarelo a partir de | Vermelho a partir de |
|---|---|---|
| Aguardando PROAD | 2 dias | 3 dias |
| Aguardando Procuradoria/Jurídico | 10 dias | 20 dias |
| Em elaboração ativa (DPGC/DFI) | 5 dias | 10 dias |
| Circulando em unidades técnicas/requisitantes | 5 dias | 10 dias |

Esses limites são práticos, definidos pela equipe (não normativos) — ajustáveis livremente no sistema.

**Urgente:** sempre manual. Nunca inferir automaticamente — só quando a pessoa sinalizar explicitamente.

## 6. Gestor (responsável)

O gestor só é exibido/rastreado **enquanto o processo está na DPGC**. Ao sair da DPGC (entrar na DFI), o campo de gestor deixa de ser mostrado — outros servidores assumem e isso não precisa de acompanhamento no painel por ora.

Gestores confirmados: Jorge Henrique Teotonio de Lima Melo, Adrielly Cristiane Silva Vital Nunes, Lucas, Pedro (confirmar se é o mesmo "Pedro da Rocha Souza" que aparece em documentos), Chianc Leocadio de Lima, Flavio Carlos de Albuquerque, Thays Lins Galvao de Albuquerque Bastos. Renato Luiz Vieira de Carvalho não trabalha mais na equipe — processos dele são reatribuídos a Jorge.

## 7. Estados especiais — detecção automática

- **Homologado:** documento tipo "HOMOLOGAÇÃO" saindo da DFE para a Diretoria de Compras → marcar fase Homologado automaticamente, e excluir das contagens de acompanhamento ativo (só aparece numa aba própria de histórico).
- **Em recurso:** documentos "RECURSO ADMINISTRATIVO DE LICITAÇÃO" + "JULGAMENTO DE RECURSO" → marcar `emRecurso: true` automaticamente, fase continua DFE.
- **Suspenso:** sempre um evento da **DFE**. Regra de detecção: toda movimentação **DFE → Diretoria de Compras** que não seja homologação nem recurso (pelos critérios acima) obriga o sistema a abrir o documento de envio dessa movimentação e ler o texto — se confirmar suspensão, marcar `suspenso: true` automaticamente. Fora desse cenário específico, nunca precisa abrir documento só para checar suspensão.

## 8. Geração do resumo de situação atual

Para cada processo, pegar no máximo os **2 documentos mais recentes** (da página mais avançada — pregão se existir, senão planejamento) + as movimentações recentes, ler o conteúdo e gerar um resumo curto em texto livre (estilo do campo "situação atual" já usado no protótipo). Não ler mais que isso — decisão explícita para não pesar o processo.

## 9. Casos de baixa confiança

Se um despacho estiver com "Acesso Negado", data ambígua, ou qualquer inconsistência de apensação: **não presumir, não registrar** — sinalizar diretamente no chat com a pessoa e perguntar. **Não** poluir o dashboard/cards com indicadores de "precisa verificar" — isso fica de fora da interface visual.

## 10. Descoberta automática de processos novos

Pipeline (roda toda sexta-feira automaticamente, e sob demanda quando a pessoa pedir):

1. Buscar no portal público (`https://sipac.ufrn.br/public/jsp/portal.jsf`, aba "Processos") por **Tipo de Processo = PLANEJAMENTO DE CONTRATAÇÃO/AQUISIÇÃO (33.00)** (option value `314`) **+ Período de Cadastro = hoje até 7 dias atrás**.
2. Percorrer **todas as páginas** de resultado (há paginação real — testado com 23 registros em 2 páginas).
3. Descartar processos cujo número/id já estejam registrados como "já vistos" (arquivo local de cache) — evita reabrir/reanalisar processo repetido.
4. Para cada processo novo: abrir a página pública e checar o **primeiro documento** da lista. Se for **"DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA DIGITAL (DFD DIGITAL)"**, é um processo válido para acompanhar — adicionar ao painel e rodar a extração de marcos (seção 3). Se não for, marcar como "visto, fora do padrão" e não tratar mais.

## 11. Limitações técnicas conhecidas do SIPAC público

- A busca pública **por número de processo/documento** (formulário "N° Processo"/"N° Documento") **não funciona via automação simples** (POST direto) — parece depender de estado de sessão JSF que não se reproduz fora de um navegador real. **Não insistir nesse caminho.**
- A busca pública **por tipo de processo/documento** (dropdown) **funciona bem via automação** — é o caminho usado para descoberta (seção 10) e também para achar processos por tipo de documento (ex.: todos os despachos de um tipo, cada um informando "Processo Associado: NNNNN" no rodapé).
- Links "Visualizar Documento" na listagem de documentos são `href="#"` com JavaScript (`onclick`), mas o `onclick` contém uma URL pública real de download (`/public/verArquivoDocumento?idArquivo=...&key=...`) que funciona sem login — já validado baixando e lendo PDFs reais de processos de planejamento e de pregão, de vários tipos de documento.
- A conexão com o SIPAC é instável (erros de "connection reset" frequentes, tanto em `curl` quanto em navegador automatizado) — qualquer automação precisa de lógica de nova tentativa (retry), tipicamente resolve em 2-4 tentativas.
- Navegador automatizado (Playwright/Chromium) teve problemas consistentes de conexão neste ambiente específico — `curl` com retry é o caminho confiável hoje.
- Não é possível abrir o processo só com o número (sem o `id=` interno) exceto pelos caminhos de busca por tipo (seção 10) — a busca direta por número não funciona.

## 12. Acesso e edição

Por enquanto: todo mundo (quando o painel for compartilhado) pode **ver** tudo. Só a pessoa dona do projeto pode **editar/adicionar** processos. Não construir controle de permissão granular por unidade agora.

## 13. Estilo de trabalho combinado

- Fazer perguntas de esclarecimento **antes** de implementar mudanças ambíguas.
- Nunca presumir vínculos entre processos (planejamento ↔ pregão) sem confirmação.
- Ao processar em lote, perguntar se deve narrar o progresso ou trabalhar silenciosamente e reportar o resultado consolidado.
- Testar empiricamente antes de afirmar uma capacidade técnica (ex.: baixar e ler um documento de verdade antes de dizer que "funciona") — várias suposições iniciais deste projeto (links de documento "mortos", busca por número, etc.) se mostraram erradas só depois de testar de fato.

## 14. Em aberto (ainda não decidido)

- Design visual do dashboard: a pessoa quer algo mais "disruptivo" que um Kanban/Trello tradicional, mas ainda não sabe exatamente o quê — vai ser por tentativa e erro.
- Arquitetura de implementação (onde/como persistir os dados dos processos, tecnologia do frontend) — ainda não definida.
- Mecanismo exato de agendamento da atualização semanal automática (ex.: rotina agendada) — a capacidade existe, falta desenhar a implementação.
