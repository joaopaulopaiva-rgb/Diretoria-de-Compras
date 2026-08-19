# Base Legal — Caminho Dispensa de Licitação

Terceiro documento da série (ver `BASE_LEGAL_PREGAO.md` para o piloto de formato). Mesma lógica: o que a norma diz, fonte oficial, data de consulta, status de verificação.

---

## 1. Lei nº 14.133/2021 — Art. 75 (Hipóteses de dispensa)

**Fonte oficial**: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm
**Status**: ⚠️ Mesma ressalva de `BASE_LEGAL_PREGAO.md` — planalto.gov.br bloqueado neste ambiente; texto vem do PDF que você enviou, lido na íntegra (art. 75 completo, incisos I a XVIII e §§ 1º a 3º e seguintes).

### Incisos mais usados na prática da UFRN (confirmado por `ANALISE_PROCESSOS.md`, seção 2)

> "Art. 75. É dispensável a licitação:
> I - para contratação que envolva valores inferiores a R$ 100.000,00 (cem mil reais), no caso de obras e serviços de engenharia ou de serviços de manutenção de veículos automotores;
> II - para contratação que envolva valores inferiores a R$ 50.000,00 (cinquenta mil reais), no caso de outros serviços e compras;
> III - para contratação que mantenha todas as condições definidas em edital de licitação realizada há menos de 1 (um) ano, quando se verificar que naquela licitação:
> a) não surgiram licitantes interessados ou não foram apresentadas propostas válidas;
> b) as propostas apresentadas consignaram preços manifestamente superiores aos praticados no mercado ou incompatíveis com os fixados pelos órgãos oficiais competentes;"

- **Inciso II é a base legal dominante** observada na amostra (`ANALISE_PROCESSOS.md`, seção 2: "Base legal dominante: art. 75-II [...] baixo valor"). Os valores de R$ 100 mil (obras/engenharia) e R$ 50 mil (demais) estão sujeitos a atualização por decreto — o próprio texto oficial lista uma sequência de decretos de atualização (10.922/2021, 11.317/2022, 11.871/2023, 12.343/2024, 12.807/2025), o que significa que **o valor vigente em qualquer momento precisa ser conferido no decreto de atualização mais recente**, não só no texto original da Lei.
- **Inciso III-b confirma um achado real e relevante** de `ANALISE_PROCESSOS.md`: *"Dispensa também é usada como saída de pregões malsucedidos, não só por valor baixo"* — ou seja, quando uma licitação (Pregão) tem preços incompatíveis com o mercado, a lei permite migrar para Dispensa mantendo as condições do edital anterior, sem reabrir do zero. Essa é provavelmente a base legal do "abandono da via de pregão" documentado em `ANALISE_PROCESSOS.md` (seção 1, farmacológicos).

### Art. 75, § 1º — Regra de aferição de valor (relevante para fiscalização/auditoria)

> "§ 1º Para fins de aferição dos valores que atendam aos limites referidos nos incisos I e II do caput deste artigo, deverão ser observados: I - o somatório do que for despendido no exercício financeiro pela respectiva unidade gestora; II - o somatório da despesa realizada com objetos de mesma natureza, entendidos como tais aqueles relativos a contratações no mesmo ramo de atividade."

- Isso significa que o limite de R$ 50 mil/R$ 100 mil **não é por processo isolado** — é o somatório do exercício financeiro para objetos de mesma natureza. Fracionamento de despesa para escapar do limite é irregularidade clássica; vale ter esse dispositivo em mente ao gerar minutas ou verificar conformidade.

### Demais incisos (IV a XVIII) — referência, não observados na amostra da UFRN

Cobrem hipóteses específicas (manutenção com exclusividade de garantia, acordos internacionais, P&D, transferência de tecnologia por ICT, gêneros perecíveis, segurança nacional/Forças Armadas, emergência/calamidade — **este é o "art. 75, VIII" citado nos modelos de contrato da AGU para vigência improrrogável de até 1 ano** —, entre outras). Nenhuma dessas hipóteses foi observada nos 30 processos de Dispensa lidos por `ANALISE_PROCESSOS.md`; ficam registradas aqui como referência para o dia em que aparecerem.

---

## 2. Ausência de Parecer Referencial dedicado da AGU para Dispensa (achado relevante)

**Status**: ✅ Verificado por leitura direta dos 10 pareceres referenciais disponíveis no site da AGU (ELIC) nesta sessão.

Diferente do caminho Pregão (Parecer 00006/2025) e da Adesão SRP (Parecer 00009/2025), **não existe, entre os 10 pareceres referenciais publicados pela ELIC/PGF/AGU até a data desta consulta, nenhum dedicado especificamente à Dispensa de Licitação por valor baixo** (art. 75, I/II). Os 10 pareceres lidos cobrem: prorrogação contratual (regimes de 2021 e de 1993), inexigibilidade para água/esgoto, inexigibilidade para energia elétrica, prorrogação de ARP, aquisições de pregão ≤R$1M, aditivo de supressão, gêneros alimentícios, adesão a ARP, jornada de trabalho.

- **Isso é coerente com o achado de `ANALISE_PROCESSOS.md`** (seção 2): *"Sem Jurídico na maioria"* dos processos de Dispensa — mas, diferente da Adesão SRP (onde a dispensa de exame jurídico tem base normativa explícita, seção 3 de `BASE_LEGAL_ADESAO_SRP.md`), aqui **não encontrei o dispositivo normativo específico que dispensaria a análise jurídica individualizada em Dispensa de baixo valor**. É possível que exista uma Orientação Normativa da AGU equivalente à ON 88/2024 (vista para SRP) cobrindo Dispensa — mas não foi localizada nesta sessão entre os documentos consultados (não testei acesso à AGU além da lista de pareceres e modelos já mapeada).
- **Recomendação**: tratar a ausência de Jurídico em Dispensa, por ora, como **prática observada** (a esmagadora maioria dos casos reais não tem parecer jurídico), não como uma dispensa formalmente confirmada em norma — diferença sutil, mas importante para não afirmar uma base legal que não foi de fato localizada. Vale pesquisa dedicada a essa lacuna específica no futuro, se você achar importante fechar esse ponto.

---

## 3. Achado de qualidade documental — Lei 8.666/93 em templates de Dispensa

**Fonte**: `ANALISE_PROCESSOS.md`, seções 2 e 7 (achado empírico, não normativo).

> "Base legal desatualizada em template: praticamente todo Parecer Técnico cita 'Lei 8.666/93' e 'art. 75-II da Lei 14.133/2021' na mesma frase — mistura de lei revogada com enquadramento correto, presente sistematicamente. [...] não é erro caso a caso, é o modelo de documento em uso."

- A Lei 8.666/93 foi **revogada** pela Lei 14.133/2021 (com período de transição encerrado). Sua citação em Parecer Técnico de Dispensa, ao lado do enquadramento correto em art. 75-II, é resíduo de template desatualizado — não vale como base legal adicional, é ruído documental sistemático a reportar para correção do modelo usado pela equipe, não algo a reproduzir em minutas novas.

---

## Resumo do que falta verificar

| Item | Situação |
|---|---|
| Lei 14.133/2021, art. 75 (integral) | ✅ Lido na íntegra, via PDF fornecido por você (fonte genuína, não acessada ao vivo) |
| Decreto de atualização dos valores de I/II vigente na data de uma contratação específica | 🔴 Não verificado nesta sessão — precisa ser checado caso a caso, o valor muda por decreto ao longo do tempo |
| Base normativa formal para dispensa de exame jurídico em Dispensa de baixo valor (equivalente à ON 88/2024 da SRP) | 🔴 Não localizada nesta sessão — pode não existir, ou pode não ter sido encontrada na busca feita |
| Acórdãos TCU eventualmente aplicáveis (fracionamento de despesa, uso de art. 75-III-b) | 🔴 Não pesquisado — mesmo bloqueio de acesso ao TCU já registrado em `BASE_LEGAL_PREGAO.md` |

---

*Terceiro documento da série — caminho Dispensa. Ver `BASE_LEGAL_PREGAO.md` para o piloto de formato.*
