# Base Legal — Caminho Contrata+Brasil

Sexto e último documento da série piloto (ver `BASE_LEGAL_PREGAO.md` para o formato). **Importante**: `CLAUDE.md` (seção 4.5) já registra que este caminho é "rascunho — baseado em fontes públicas, ainda não confirmado com processos reais da UFRN". Esta pesquisa **encontrou a norma oficial do programa pela primeira vez** (não localizada nas sessões anteriores que geraram o rascunho do `CLAUDE.md`) — o achado abaixo **resolve, com base normativa, uma pergunta que ficou em aberto em `ANALISE_PROCESSOS.md`** (seção 8, item 2). Mesmo assim, mantenho a recomendação de tratar como preliminar até confirmar com mais processos reais, como o próprio `CLAUDE.md` já pedia.

---

## 1. Achado principal — mecanismo é Credenciamento, não Dispensa

**Fonte oficial**: https://www.gov.br/contratamaisbrasil/pt-br/central-de-conteudo/editais-e-regulamentacao
**Status**: ✅ Acessada ao vivo nesta sessão. Nota técnica: o mesmo conteúdo normativo, quando buscado pela URL espelhada em gov.br/compras, retornou **HTTP 401 Unauthorized** (testado via `curl` e `WebFetch`) — o portal correto e público é `gov.br/contratamaisbrasil`, subsite próprio do programa, não a área geral de legislação do gov.br/compras. Fica registrado porque pode ser útil para buscas futuras.

**O achado**: a Instrução Normativa SEGES/MGI nº 52/2025 (10/02/2025), que cria a plataforma Contrata+Brasil, estabelece em seu **art. 2º** que os bens e serviços são disponibilizados **"por meio de credenciamento, outros procedimentos auxiliares e chamadas públicas"** — não menciona dispensa (art. 75) como fundamento.

- **Credenciamento é hipótese de inexigibilidade**, prevista no **art. 74, IV, da Lei 14.133/2021** ("objetos que devam ou possam ser contratados por meio de credenciamento") e detalhada no **art. 79** (já lido na íntegra para `BASE_LEGAL_INEXIGIBILIDADE.md` — hipóteses de credenciamento paralelo e não excludente, seleção a critério de terceiros, mercados fluidos, comércio eletrônico).
- **Isso confirma, com base normativa, o achado empírico de `ANALISE_PROCESSOS.md`** (seção 6): *"Nos 2 processos lidos, a Nota de Empenho cita Modalidade: INEXIGIBILIDADE (Lei 14.133/2021, Art. 74, IV) — não o art. 75 (dispensa) que era a base legal esperada pelas fontes públicas genéricas"*. A pergunta em aberto que `ANALISE_PROCESSOS.md` registrava (seção 8, item 2: "é a regra do programa ou peculiaridade desses 2 casos?") **tem agora resposta normativa**: é a regra do programa, não peculiaridade — a IN 52/2025 estabelece credenciamento como mecanismo, e credenciamento é inexigibilidade por força do art. 74, IV.
- Fontes públicas genéricas sobre o programa (usadas para montar o rascunho original do `CLAUDE.md`, antes desta pesquisa) mencionavam "dispensa eletrônica com base no art. 75" — **essa informação genérica estava desatualizada ou imprecisa**; a norma oficial do programa (IN 52/2025 + sua alteração, IN 460/2025) não usa esse enquadramento.

---

## 2. Instrução Normativa SEGES/MGI nº 52/2025 (norma-base do programa)

**Fonte oficial**: https://www.gov.br/contratamaisbrasil/pt-br/central-de-conteudo/editais-e-regulamentacao/instrucoes-normativas/instrucao-normativa-seges-mgi-no-52-de-10-de-fevereiro-de-2025
**Status**: ✅ Acessada ao vivo nesta sessão (via WebFetch — não li o texto artigo por artigo na íntegra como fiz com a Lei 14.133/Decreto 11.462 em PDF; o que segue é um resumo estruturado do conteúdo obtido).

- **Público-alvo** (art. 13): tratamento favorecido a microempresas (ME), empresas de pequeno porte (EPP), agricultor familiar, produtor rural pessoa física, microempreendedor individual (MEI) e sociedades cooperativas — **mais amplo do que "só MEI"**, como o rascunho anterior do `CLAUDE.md` (baseado em fontes genéricas) sugeria.
- **Prioridade local/regional** (art. 18): fornecedores locais/regionais têm prioridade quando a proposta estiver até 10% acima da concorrente — mecanismo de fomento regional embutido na norma.
- **Limite de valor**: a versão original previa R$ 80 mil, mas **foi alterada** (ver IN 460/2025 abaixo) — a redação vigente não fixa mais um teto único no corpo da norma, delegando a regramento específico por edital/objeto. **Ponto de atenção**: qualquer limite de valor citado em processo precisa ser conferido contra a versão vigente na data da contratação, não presumido.
- **Fluxo operacional** (arts. 10-29): fase preparatória → divulgação → registro de demanda → seleção de fornecedores → verificação de habilitação → assinatura (preferencialmente digital) → pagamento (preferencialmente via PIX) → monitoramento.

---

## 3. Instrução Normativa SEGES/MGI nº 460/2025 (altera a IN 52/2025)

**Fonte oficial**: https://www.gov.br/contratamaisbrasil/pt-br/central-de-conteudo/editais-e-regulamentacao/instrucoes-normativas/instrucao-normativa-seges-mgi-no-460-de-31-de-outubro-de-2025
**Status**: ✅ Acessada ao vivo nesta sessão (mesma ressalva do item 2 — resumo estruturado, não leitura artigo por artigo).

Publicada em 31/10/2025 — **posterior aos 2 processos reais da UFRN lidos em `ANALISE_PROCESSOS.md` (levantamento até agosto/2026, mas os 2 casos específicos não têm data individual registrada)**. Vale conferir, ao ler novos processos de Contrata+Brasil daqui para frente, se eles já refletem esta versão alterada ou ainda a redação original de fevereiro/2025.

Principais mudanças identificadas:
- **Art. 2º reformulado**: confirma explicitamente "credenciamento, outros procedimentos auxiliares e chamadas públicas" como mecanismo (reforça o achado da seção 1).
- **Art. 15**: passa a **dispensar análise de riscos, termo de referência e edital**, e permite dispensar o Estudo Técnico Preliminar (ETP) mediante certificação — **isso bate diretamente** com o achado de `ANALISE_PROCESSOS.md` (seção 6): *"sem DFD/ETP/TR próprios (esses vêm prontos da plataforma federal)"*. Agora há base normativa explícita para essa ausência, não é só um padrão observado.
- **Art. 9º**: acrescenta obrigações para órgãos gestores (manter informações atualizadas, instaurar contraditório, notificar irregularidades).
- Ajustes processuais em arts. 21-24, 32, 38-39: prazos de manifestação (2-5 dias úteis), assinatura digital, pagamento via PIX, causas de inativação temporária de fornecedor.

---

## Resumo do que falta verificar

| Item | Situação |
|---|---|
| IN SEGES/MGI nº 52/2025 | ✅ Acessada ao vivo nesta sessão (resumo estruturado via WebFetch, não leitura integral artigo por artigo) |
| IN SEGES/MGI nº 460/2025 (altera a 52/2025) | ✅ Acessada ao vivo nesta sessão (idem) |
| Lei 14.133/2021, art. 74, IV e art. 79 (credenciamento) | ✅ Já lidos na íntegra para `BASE_LEGAL_INEXIGIBILIDADE.md` |
| **Recomendação principal**: confirmar com mais processos reais da UFRN se o enquadramento em credenciamento/inexigibilidade (art. 74, IV) é sistemático, agora que há base normativa que aponta nessa direção | 🔴 Só 2 processos lidos até agora (`ANALISE_PROCESSOS.md`, seção 6) — `CLAUDE.md` já registrava essa necessidade antes desta pesquisa, e ela continua de pé |
| Texto artigo por artigo completo das duas INs (li resumo estruturado, não o texto legal linha a linha como fiz com a Lei 14.133 e o Decreto 11.462) | 🔴 Pendente, se você quiser esse nível de detalhe |

---

*Sexto documento da série — caminho Contrata+Brasil. Ver `BASE_LEGAL_PREGAO.md` para o piloto de formato. Este é o único dos 6 documentos com achado que diverge do rascunho anterior do `CLAUDE.md` — vale sua atenção específica antes de eu considerar isso "fechado".*
