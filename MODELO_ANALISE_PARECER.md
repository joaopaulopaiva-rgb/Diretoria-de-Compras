# Modelo — Análise de Parecer Jurídico

Despacho formal emitido pela **Diretoria de Compras/PROAD (11.02.09)**, em resposta a um Parecer
Jurídico (PGF/AGU) que condicionou o prosseguimento do certame ao atendimento de itens/ressalvas
numerados. Aprendido e validado em 28/09/2026, a partir de quatro documentos reais assinados por
João Paulo Paiva da Silva (Diretor - Titular): processos 23077.079577/2024-31, 23077.065173/2024-61,
23077.049893/2024-89 e 23077.084268/2024-83.

**Correção de rumo:** a primeira geração automatizada desse produto (28/09/2026, processo
23077.117613/2025-53) usou um formato de prosa livre em 4 parágrafos (resumo do parecer +
recomendação genérica) — **estrutura errada**, apontada pelo João. Este documento registra a
estrutura correta para não repetir o erro.

---

## 1. Estrutura do documento

Documento corrido, sem quadros/faixas (ao contrário da Certificação Processual). Cabeçalho
centralizado, sem negrito:
```
MINISTÉRIO DA EDUCAÇÃO
UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
DIRETORIA DE COMPRAS - PROAD
```

Em seguida (alinhado à esquerda, negrito no título):
- **ANÁLISE DE PARECER JURÍDICO Nº XX/AAAA - COMPRAS/PROAD (11.02.09)** — numeração sequencial
  interna da Diretoria; a pessoa quem preenche/protocola, não é gerada automaticamente (deixar
  `Nº ___/AAAA` na minuta quando não souber o próximo número da sequência).
- **Nº do Protocolo:** nos 4 exemplos, sempre "NÃO PROTOCOLADO" — manter esse valor por padrão.
- Data por extenso, alinhada à direita: "Natal-RN, DD de mês de AAAA."
- **PROCESSO:** número do processo.
- Descrição do objeto em CAIXA ALTA, uma ou duas linhas (mesmo texto/estilo do cabeçalho do
  processo no SIPAC).

Título de seção (centralizado, negrito): **ANÁLISE DE PARECER JURÍDICO** — em dois dos quatro
exemplos aparece como **DESPACHO** em vez disso; não há um critério claro sobre quando usar um ou
outro — usar "ANÁLISE DE PARECER JURÍDICO" como padrão, e perguntar ao João se ele preferir o outro
título num caso específico.

### Corpo

1. **Parágrafo de abertura** (fórmula fixa, adaptar apenas os dados do parecer e a lista de itens):
   > "Da leitura do PARECER n. [número]/[NLC/ELIC ou NLC/ETRLIC]/PGF/AGU, constante no documento
   > [N] dos autos em epígrafe, exsurge ter sido condicionado o seguimento do feito ao atendimento
   > dos itens [lista], tendo o citado sido devidamente homologado pela Pró-Reitoria de
   > Administração."
   - Se o parecer concluiu por "regularidade, com ressalvas" sem homologação prévia da PROAD
     (caso mais comum no fluxo atual do Pregão — ver CLAUDE.md §3), ajustar a frase final para
     algo como "ressalvado o mérito técnico, econômico e financeiro da Administração" (fórmula já
     usada nas análises anteriores desta sessão) em vez de citar homologação que ainda não
     ocorreu — não copiar a cláusula de homologação se ela não for verdadeira no caso.

2. **Parágrafo de transição** (fórmula fixa, sempre igual nos 4 exemplos):
   > "Passamos, portanto, a relatar as providências adotadas em atendimento às recomendações
   > exaradas no citado Parecer Jurídico, condições essenciais ao prosseguimento do presente
   > certame licitatório."

3. **Um item por letra (a, b, c, ...)** — um item do parecer (ou um pequeno grupo de itens
   correlatos) por letra, cada um com:
   - "Item(ns) NN [e NN] do parecer:" (sublinhado nos originais) seguido de dois pontos.
   - A resposta ao item: ou (i) uma justificativa/esclarecimento que a própria Diretoria já pode
     dar diretamente (ex.: fundamentar o uso do SRP, justificar concentração do objeto), ou (ii) o
     encaminhamento do item para a unidade responsável por produzir o ajuste (DPGC, DFI, PROAD,
     conforme o que o item pede e em que fase do processo ele se encontra).
   - Cada letra pode ter mais de um parágrafo, mas cada parágrafo fica em uma linha só (sem quebra
     manual no meio da frase — regra geral do projeto, CLAUDE.md §9).

4. **Parágrafo de fechamento** — consolida o encaminhamento: reúne as letras que vão para a mesma
   unidade numa única frase, e usa o registro de despacho oficial (regra fixa do projeto, CLAUDE.md
   §16): fechar a frase anterior com ponto, começar frase nova, verbo no imperativo/subjuntivo de
   determinação ("remeta-se", "retornem os autos", "encaminhem-se"), nunca "encaminham-se" emendado
   com ponto e vírgula. Ex.: "Deste modo, remeta-se o feito à DPGC para atendimento dos itens "a" e
   "b" deste parecer. Em seguida, remeta-se o feito à DFI para atendimento do item "d". Por fim,
   retornem os autos à direção para análise e seguimento."
   - Pode haver um parágrafo extra "Em tempo," depois do fechamento, para um pedido acessório sem
     relação direta com o parecer (visto em 1 dos 4 exemplos) — só incluir se houver algo real para
     registrar, não é parte fixa da estrutura.

5. **Assinatura** (documento já emitido) ou **"(A ser assinado digitalmente)"** (minuta ainda não
   protocolada):
   ```
   JOAO PAULO PAIVA DA SILVA
   DIRETOR - TITULAR
   COMPRAS/PROAD (11.02.09)
   ```

6. **Rodapé:** "Processo Associado: [número]" — sempre presente.

## 2. O que NÃO fazer

- Não escrever um resumo/prosa livre do parecer (o erro cometido na primeira geração automatizada)
  — o produto é um **despacho de encaminhamento formal**, item por item, não uma análise narrativa
  solta.
- Não inventar o número sequencial "Nº XX/AAAA" nem "protocolar" a minuta — isso é decisão de quem
  assina.
- Não citar homologação da PROAD como fato consumado se ela ainda não ocorreu no processo em
  questão (ver nota na seção 1, item 1).

## 3. Aplicação na rotina automática (`analise_parecer`)

Este modelo substitui a instrução antiga ("escreva uma ANÁLISE objetiva") no passo 2/letra e das
12 rotinas "Processar certificações" quando o documento-fonte vencedor é um PARECER (mantém-se a
instrução antiga — minuta de despacho de encaminhamento — para o caso NOTA INFORMATIVA, que já
estava correto). Adaptado em 28/09/2026, junto com a correção do caso real do processo
23077.117613/2025-53.
