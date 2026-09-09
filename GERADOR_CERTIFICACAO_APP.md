# Gerador de Certificação Processual da UFRN — o "sisteminha"

Página onde João e Edjane digitam um número de processo e recebem de volta o PDF da
Certificação Processual (modelo documentado em `MODELO_CERTIFICACAO_PROCESSUAL.md`),
sem precisar abrir o SIPAC manualmente. Criado em 09/09/2026, a pedido de João
("Quero que voce monte o sisteminha e ja deixe pronto [...] Nao precisa de login e senha").

**Página (Artifact, sem login):** https://claude.ai/code/artifact/c0f6ffd2-50be-4cae-a772-38f685de0706

---

## 1. Por que não é instantâneo

A página roda no navegador de quem usa, e o navegador não consegue acessar o SIPAC
diretamente (bloqueio de CORS — a mesma limitação que já existia pro painel de compras
em si). Não dá pra fazer "digitou o número → o próprio navegador busca no SIPAC e devolve
o PDF" sem um backend.

A solução: a página só escreve/lê num banco compartilhado (capability `db` do Artifact,
ver seção 2). Quem faz o trabalho pesado (abrir o SIPAC, montar o PDF) é uma rotina
agendada (Routine) que roda com acesso real à internet — o intervalo mínimo permitido
pra esse tipo de agendamento é de **1 hora**. Isso está avisado na própria página, na
seção "Como funciona".

## 2. Arquitetura

```
Edjane/João → página (Artifact) → grava em db "solicitacoes" (status: pendente)
                                          ↓
                    Routine dispara a cada hora (cron "36 * * * *")
                                          ↓
        sessão do Claude Code roda scripts/gerar_certificacao.py contra o SIPAC
                                          ↓
                    grava resultado de volta no mesmo doc (status: pronto/erro)
                                          ↓
              página atualiza sozinha (onSnapshot) → botão "Baixar PDF" aparece
```

### Banco de dados (capability `db` do Artifact)

Coleção **`solicitacoes`** — um documento por pedido:
- `numero`, `tipo` (pregao/dispensa/inexigibilidade/adesao_srp/concorrencia)
- `nome`, `cargo`, `solicitante` — opcionais, texto livre
- `status`: `pendente` → `processando` → `pronto` **ou** `erro`
- `criadoEm`, `processadoEm` — ISO 8601
- `avisos` — lista de strings (campos que o script não conseguiu confirmar com
  segurança e por isso deixou em branco no PDF; ver `MODELO_CERTIFICACAO_PROCESSUAL.md`)
- `erro` — mensagem, só quando `status = erro`
- `pdfBase64`, `pdfNome` — só quando `status = pronto`

Coleção **`relatos`** — um documento por relato de erro que alguém reportar no card
do pedido ("Relatar um problema" na página):
- `solicitacaoId` (id do doc em `solicitacoes`), `numero`, `texto`, `criadoEm`
- `revisado`: `false` até a rotina processar/eu ler; vira `true` depois.

### Routine

- Nome: **"Processar fila — Gerador de Certificação Processual"**
- `trigger_id`: `trig_01N1drupA9E7Cg9zLSQVkNUH`
- Cron: `36 * * * *` (a cada hora, minuto 36 — ancorado no minuto de criação)
- Amarrada a esta mesma sessão (self-bind) — cada disparo aparece como uma
  notificação/turno nesta conversa.
- O que ela faz a cada disparo: lê `solicitacoes` com `status == pendente`, roda
  `python3 scripts/gerar_certificacao.py "<numero>" --tipo <tipo> [--nome] [--cargo]`
  pra cada um, grava o resultado de volta, depois lê `relatos` com `revisado == false`.
  Só gera mensagem no chat se achou relato novo ou se algum processamento deu erro —
  fila vazia processada com sucesso não gera nenhum aviso (silencioso por design).
- Testada de ponta a ponta em 09/09/2026 (pedido sintético na fila → disparo manual
  via `fire_trigger` → PDF voltou idêntico, byte a byte, ao gerado localmente).

## 3. Bug real encontrado e corrigido durante o teste

O `pymupdf`, ao ser importado como `import fitz` (nome antigo), imprime um aviso de
depreciação **no stdout**, na frente do JSON que o script devolve — isso quebra
qualquer leitura automatizada do resultado (`json.loads` falha porque a primeira
linha não é JSON). Como a Routine depende de capturar o stdout do script como JSON,
esse bug travaria a fila silenciosamente. Corrigido trocando pra `import pymupdf as
fitz` (nome atual, não emite o aviso).

## 4. Sem login — o que isso significa na prática

A pedido explícito de João. Qualquer pessoa com o link da página consegue enviar
pedidos e ver a fila inteira (não só os próprios pedidos) — o link é o único controle
de acesso. Como os dados de origem (SIPAC público) já não exigem login pra serem
vistos, o risco é baixo, mas vale lembrar: não é um controle de acesso real, é
"link não-listado".

## 5. Como atualizar a página

O arquivo-fonte fica no scratchpad da sessão que a criou (não versionado no repo —
é só HTML/JS do Artifact, não faz sentido commitar junto do código Python). Pra
mudar algo na página: reabrir a URL do Artifact com `action: "read"`, editar,
publicar de novo passando o mesmo `url` (mantém o link).

## 6. Em aberto

- Ainda não testado com Dispensa/Inexigibilidade/Adesão SRP/Concorrência de verdade
  pela página (só Pregão, que já era o caso validado em
  `MODELO_CERTIFICACAO_PROCESSUAL.md`).
- Ainda não testado um pedido real de João/Edjane esperando o disparo natural da
  Routine (só disparo manual, forçado).
- `relatos` fica sob demanda de eu ler manualmente quando a Routine dispara — não há
  hoje nenhuma notificação push além disso.
