# Gerador de Certificação Processual da UFRN — o "sisteminha"

Página onde João e Edjane digitam um número de processo e recebem de volta o PDF da
Certificação Processual (modelo documentado em `MODELO_CERTIFICACAO_PROCESSUAL.md`),
sem precisar abrir o SIPAC manualmente. Criado em 09/09/2026, a pedido de João
("Quero que voce monte o sisteminha e ja deixe pronto [...] Nao precisa de login e senha").

**Página (Artifact, sem login):** https://claude.ai/code/artifact/c0f6ffd2-50be-4cae-a772-38f685de0706

**Importante — leia antes de mexer na UI:** a primeira versão usava linguagem de "fila"
(campo "quem está pedindo", botão "Enviar pra fila", seção "Fila e histórico"). João
rejeitou esse modelo explicitamente ("não tem fila, não tem rodar periodicamente. É com
início e fim") — a versão atual não fala em fila em lugar nenhum da interface: é um botão
"Gerar Certificação" e um histórico único onde o card já nasce "Gerando" e vira "Pronto"
sozinho. Por trás continua sendo assíncrono (ver seção 1), mas isso fica invisível na
UI — não reintroduzir o vocabulário de fila numa próxima edição sem falar com ele antes.

---

## 1. Por que não é instantâneo (e por que não dá pra ser)

A página roda dentro do sandbox de uma Artifact, que **não tem acesso a rede nenhum** —
nem fetch, nem XHR, nem WebSocket, pra host nenhum (isso foi checado explicitamente
nesta sessão, não é suposição). As únicas pontes pro mundo são as capabilities que a
plataforma libera (`db`, `downloads`, etc.). Então "digitou o número → a própria página
busca no SIPAC" é impossível, independente de arquitetura — não é um bloqueio de CORS
contornável com um servidor próprio de CORS liberado, é uma trava de sandbox da própria
Artifact.

Cogitamos (e descartamos, todos por razões concretas, não só teóricas):
- **Servidor externo de verdade** (ex.: Render/Railway/Fly.io) — resolveria de verdade,
  mas exige criar conta de hospedagem. João foi explícito: não quer mexer com isso.
- **Edjane conversar direto comigo (chat)** — seria instantâneo, mas exige conta
  Claude pra ela, que João também não quer.
- **`watch_url` (webhook)** — a página ainda não consegue chamá-lo (mesma trava de rede),
  e a inscrição de "avisar quando alguém comenta na Artifact" nem registrou neste
  ambiente (erro `relay_unavailable`, gateway retornou 404) — testado e confirmado.
- **`CronCreate`** (agendamento mais fino, minutos) — descartado por não ser durável:
  o job desaparece sozinho se esta sessão reiniciar, o que quebraria o sisteminha da
  Edjane sem aviso nenhum.

Dado que restavam só "banco compartilhado (`db`) + processamento por alguém com acesso
à internet de verdade", a única forma de eu processar isso é: (a) ao vivo numa conversa,
ou (b) por uma Routine agendada — cujo intervalo mínimo por rotina individual é 1 hora.

## 2. Arquitetura

```
Edjane/João → página (Artifact) → grava em db "solicitacoes" (status: pendente)
                                          ↓
      6 Routines escalonadas disparam a cada ~10min (seg-sex, 8h-17h, sem 12h30-13h30)
                                          ↓
        sessão do Claude Code roda scripts/gerar_certificacao.py contra o SIPAC
                                          ↓
                    grava resultado de volta no mesmo doc (status: pronto/erro)
                                          ↓
              página atualiza sozinha (onSnapshot) → botão "Baixar PDF" aparece
```

### Por que 12 rotinas em vez de 1

A trava de "mínimo 1 hora" vale **por rotina individual**, não no total — criar
múltiplas rotinas hourly, cada uma com um minuto de disparo diferente, é uma forma
legítima (não um hack) de reduzir o intervalo efetivo. Primeira versão (09/09/2026):
6 rotinas de 10 em 10 minutos (espera máxima ~10min). Ajustado no mesmo dia pra 12
rotinas de 5 em 5 minutos (espera máxima ~5min), a pedido de João, depois de confirmar
que o custo extra (o dobro de disparos "olhando fila vazia") era aceitável.

Também por pedido de João, as rotinas só disparam em horário comercial (seg-sex,
8h-17h horário de Natal-RN, pulando o almoço 12h30-13h30) — evita gastar disparos à toa
de madrugada/fim de semana, quando ninguém vai estar usando mesmo. Um disparo que acha a
fila vazia é barato (só duas consultas ao banco, sem rodar o script), mas gastar
disparos à toa fora do expediente era desnecessário.

### Banco de dados (capability `db` do Artifact)

Coleção **`solicitacoes`** — um documento por pedido:
- `numero`, `tipo` (pregao/dispensa/inexigibilidade/adesao_srp/concorrencia)
- `nome`, `cargo` — opcionais, texto livre (não existe mais campo de "quem pediu" —
  removido a pedido de João, a interface não distingue João de Edjane)
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

### Routines (12, escalonadas)

Todas com o mesmo prompt/lógica, só o cron muda. Substituíram a rotina única original
(`trig_01N1drupA9E7Cg9zLSQVkNUH`, deletada em 09/09/2026) e depois a versão de 6
rotinas (mantidas, só somaram-se mais 6):

| Minuto | `trigger_id` | Cron (UTC) |
|---|---|---|
| :04 | `trig_01SqBwdTk2iTFWnsXD8MJGyb` | `4 11-15,17-20 * * 1-5` |
| :09 | `trig_01TEAG6miifKMBPgV8aZPGcV` | `9 11-15,17-20 * * 1-5` |
| :14 | `trig_018FSsQS26tBaYHcEUxwEr25` | `14 11-15,17-20 * * 1-5` |
| :19 | `trig_014H23Qy8rZwUGQHSnf8vF7n` | `19 11-15,17-20 * * 1-5` |
| :24 | `trig_01DP1WdhERKfHdU7bd5GCo6N` | `24 11-15,17-20 * * 1-5` |
| :29 | `trig_01NwMe5sattzUY69LN8jtZWx` | `29 11-15,17-20 * * 1-5` |
| :34 | `trig_01G2qS5PTJ3yWvKksTEDYRDh` | `34 11-14,16-20 * * 1-5` |
| :39 | `trig_01DfCavXriyuWuRaKreeun1P` | `39 11-14,16-20 * * 1-5` |
| :44 | `trig_019hGwR7UsiMywjtovYiVdER` | `44 11-14,16-20 * * 1-5` |
| :49 | `trig_01NQuTvQnFp3DXFDCoebWcDx` | `49 11-14,16-20 * * 1-5` |
| :54 | `trig_018GLy9SBY8YfsRDf6cy6KP6` | `54 11-14,16-20 * * 1-5` |
| :59 | `trig_01BwfhzDSwryFZThommJcNLJ` | `59 11-14,16-20 * * 1-5` |

Os dois grupos de hora (`11-15,17-20` vs `11-14,16-20`) existem pra excluir só a janela
exata 12h30-13h30 local: os minutos <30 (:04,:09,:14,:19,:24,:29) incluem a hora 12
UTC-ajustada e excluem a 13; os minutos ≥30 (:34,:39,:44,:49,:54,:59) fazem o oposto —
juntos, nenhum disparo cai
dentro do almoço. Horário local Natal-RN = UTC-3 (sem horário de verão); por isso os
campos de hora no cron já vêm somados em +3 em relação ao horário local 8h-17h.

- Todas amarradas a esta mesma sessão (self-bind) — cada disparo aparece como uma
  notificação/turno nesta conversa.
- O que cada uma faz ao disparar: lê `solicitacoes` com `status == pendente`, roda
  `python3 scripts/gerar_certificacao.py "<numero>" --tipo <tipo> [--nome] [--cargo]`
  pra cada um, grava o resultado de volta, depois lê `relatos` com `revisado == false`.
  Só gera mensagem no chat se achou relato novo ou se algum processamento deu erro —
  fila vazia processada com sucesso não gera nenhum aviso (silencioso por design).
- A versão com rotina única (1/hora, 24/7) foi testada de ponta a ponta em 09/09/2026
  (pedido sintético → disparo manual via `fire_trigger` → PDF voltou idêntico, byte a
  byte, ao gerado localmente) antes de ser substituída pelas 6 — a lógica interna não
  mudou, só o agendamento.

## 3. Bug real encontrado e corrigido durante o teste

O `pymupdf`, ao ser importado como `import fitz` (nome antigo), imprime um aviso de
depreciação **no stdout**, na frente do JSON que o script devolve — isso quebra
qualquer leitura automatizada do resultado (`json.loads` falha porque a primeira
linha não é JSON). Como a Routine depende de capturar o stdout do script como JSON,
esse bug travaria a fila silenciosamente. Corrigido trocando pra `import pymupdf as
fitz` (nome atual, não emite o aviso).

## 4. Sem login — o que isso significa na prática

A pedido explícito de João. Qualquer pessoa com o link da página consegue gerar
certificações e ver o histórico inteiro (não só os próprios pedidos) — o link é o único
controle de acesso. Como os dados de origem (SIPAC público) já não exigem login pra
serem vistos, o risco é baixo, mas vale lembrar: não é um controle de acesso real, é
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
