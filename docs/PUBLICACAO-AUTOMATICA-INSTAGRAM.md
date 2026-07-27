# Publicação Automática no Instagram — Bônus opcional do Setup 7

> **Isto é um bônus.** Não entra na contagem das 8 etapas, não bloqueia nada e pode ser feito
> a qualquer momento — inclusive semanas depois de você terminar o Setup.
>
> **Você não precisa digitar nada no terminal.** É só pedir pro Claude: *"quero ativar a publicação
> automática no Instagram"*. Ele roda tudo por você. Este documento existe pra você entender o que
> está acontecendo e resolver sozinho se algo travar.

---

## Como ler os selos deste guia

Este produto foi derivado de um pipeline que publica Reels todo dia em produção. Nem tudo aqui tem
o mesmo grau de certeza, então cada trecho vem marcado:

| Selo | O que significa |
|---|---|
| **[COMPROVADO]** | Está rodando em produção hoje. Se der diferente na sua máquina, é bug nosso — reporte. |
| **[ALTA]** | Comportamento conhecido da API, mas não exercitado toda hora. Muito provavelmente é isso. |
| **[CONFIRA NA TELA]** | Depende de um painel da Meta. A Meta renomeia botão e menu sem avisar — o caminho abaixo é o mapa, não a foto. |
| **[VERIFICAR]** | Hipótese razoável, sem confirmação empírica nossa. Trate como pista, não como verdade. |

---

## 1. O que é (e o que não é)

**É:** publicação automática de **1 Reel por dia** no seu Instagram, usando a API oficial da Meta.
Você joga os MP4s numa fila, escreve a legenda de cada um, e o seu Mac publica sozinho no horário
que você escolher.

**Não é:**

- ❌ Não publica **Stories, Feed de foto ou Carrossel** — só Reels. É o único fluxo que temos
  comprovado de ponta a ponta, e não colocamos no seu produto código que não rodou de verdade.
- ❌ Não escreve legenda por você. Cada vídeo só é publicado se você tiver escrito o texto dele.
  Nada vai pro seu perfil com palavra que você não digitou.
- ❌ Não é automação de comentário → DM, nem responde mensagem, nem segue ninguém.
- ❌ Não é agendador em nuvem. Roda no **seu Mac** — se ele estiver desligado na hora, não posta.

---

## 2. Pré-requisitos

São 4 (mais um detalhe de máquina):

1. **Conta Instagram Business ou Creator.**
   Conta pessoal não publica por API — é limitação da Meta, não nossa. A conversão é **grátis** e
   leva 1 minuto no próprio app: *Configurações → Tipo de conta e ferramentas → Mudar para conta
   profissional*. **[CONFIRA NA TELA]** — o Instagram mexe nesse menu com frequência.
2. **Uma conta no Meta for Developers** (developers.facebook.com) com um App criado. É grátis.
3. **Um token de longa duração do Instagram** — é a "chave" que autoriza o seu Mac a postar no seu
   perfil. A seção 3 é o passo a passo.
4. **Uma URL pública HTTPS pra hospedar o vídeo.** A API da Meta **não aceita upload de arquivo do
   seu computador**: você entrega um link, e o servidor da Meta baixa o vídeo daquele link. Seção 6.

E o detalhe: **o Mac precisa estar ligado e acordado no horário do post.** Sem servidor, sem mágica.

---

## 3. Passo a passo até ter o token

> **Por que esta seção tem tantos [CONFIRA NA TELA]:** o consumo do token e a renovação dele estão
> comprovados no nosso pipeline. A **criação inicial** do token acontece dentro do painel da Meta,
> num navegador — nenhum script nosso passa por ali, então não temos como garantir o nome exato dos
> botões hoje. A sequência de ações abaixo é estável; os rótulos, não.
>
> **Nunca mexeu no Meta for Developers?** Vale assistir ao **vídeo de apresentação do Setup de
> Tráfego Pago** como apoio: nele o Rafael mostra como conectar sua conta Meta e gerar um token, e
> isso serve pra você perder o medo do ambiente da Meta. **Atenção:** lá o objetivo são permissões de
> **anúncios**, e o fluxo mostrado **não é o mesmo** desta seção — as telas do Instagram são as
> descritas abaixo. **O passo a passo do Instagram é este documento aqui**, não o vídeo.

**A sequência é sempre esta:**

**3.1 — Converta a conta** pra Business ou Creator (pré-requisito 1). Faça isso primeiro: o App não
enxerga conta pessoal.

**3.2 — Crie um App** em developers.facebook.com → *My Apps* → *Create App*. **[CONFIRA NA TELA]**
Quando ele perguntar o tipo/caso de uso, escolha o que fala em **Instagram**. Se aparecer uma opção
com "outro / other", ela costuma ser a mais flexível.

**3.3 — Adicione o produto Instagram ao App.** Nas versões recentes ele aparece como
*Instagram* → *API setup with Instagram login* (já se chamou "Instagram Basic Display" e
"Instagram Graph API" no passado). **[CONFIRA NA TELA]** — se o nome estiver diferente, procure o
card que fala em *Instagram* + *login*.

**3.4 — Conecte a sua conta e autorize as permissões.** Você vai fazer login com o seu Instagram e
aprovar o acesso. As duas permissões que importam: **[VERIFICAR]**

- `instagram_business_basic` — ler os dados básicos da conta
- `instagram_business_content_publish` — publicar conteúdo

Sem a segunda, tudo funciona até a hora de postar e aí falha com erro de permissão.

**3.5 — Gere o token de longa duração.** Na mesma tela costuma haver um botão de gerar/copiar token
(*Generate token*). **[CONFIRA NA TELA]** O que você quer é o **long-lived** (60 dias), não um token
de teste de 1 hora. Se a tela oferecer os dois, pegue o de 60 dias.

**3.6 — Pegue o seu IG_USER_ID.** É o ID numérico da sua conta Instagram (não é o @arroba). Ele
costuma aparecer na mesma tela de configuração do Instagram no App. **[CONFIRA NA TELA]**

> **Não achou o ID? Tudo bem.** Deixe o campo do ID em branco e passe só o token: a configuração
> pergunta o ID pra própria Meta usando o seu token (`GET /me?fields=user_id,username`) e preenche
> sozinha. **[VERIFICAR]** — esse endereço de consulta não é exercitado pelo nosso pipeline de
> produção. Se ele não responder, o script te diz isso na hora e volta a pedir o ID na mão; ele nunca
> trava por causa disso.

**3.7 — Se o App estiver em "Development Mode"** (o padrão de todo App novo), pode ser necessário
adicionar a sua própria conta do Instagram como **tester** dentro do App pra ela aceitar publicar.
**[VERIFICAR]** — é o suspeito nº1 quando as permissões estão certas e mesmo assim dá "permissão
negada".

**Ao final você tem 2 valores.** Não cole em lugar nenhum público, não mande por WhatsApp, não
guarde em bloco de notas na nuvem. Só entregue pro Claude quando ele pedir.

---

## 4. Ciclo de vida do token — leia isto **[COMPROVADO]**

Este é o ponto onde quase todo mundo se queima meses depois. É simples:

- O token de longa duração vale **60 dias**.
- Ele pode ser **renovado**, e a renovação só funciona quando o token tem **mais de 24 horas e menos
  de 60 dias** de idade. Antes de 24h a Meta recusa; depois de 60 dias já era.
- Renovar **1x por semana mantém o token vivo pra sempre.** É exatamente isso que o agendamento
  semanal do bônus faz por você.
- **Passou dos 60 dias sem renovar, renovação NÃO resolve.** Aí não tem jeito: você refaz o login do
  passo 3.4 e gera um token novo. Não é bug, é como a Meta funciona.

Consequência prática: **se o seu Mac ficar semanas desligado, o token morre.** Está documentado
como limitação real na seção 11.

---

## 5. Onde o token fica salvo

Em `~/.operacao-ia/config/instagram.env`, com permissão `600` (só o seu usuário lê).

Três regras:

- 🔒 **Esse arquivo fica FORA do repositório.** Nunca vai pro Git, nem por acidente.
- 🔒 O arquivo `automations/instagram/instagram.env.example` que existe dentro do projeto é só o
  **molde**, com campos vazios. **Nunca cole o seu token nele** — ele é versionado e viraria público.
- 🔒 O token fica em texto plano no seu Mac (não usamos Keychain nesta versão). Qualquer programa
  rodando com o seu usuário consegue ler. É um risco residual e estamos sendo honestos sobre ele:
  se o token vazar, revogue o App no Meta for Developers e gere outro.

As chaves guardadas ali:

| Chave | Pra que serve |
|---|---|
| `IG_USER_ID` | ID numérico da sua conta |
| `IG_ACCESS_TOKEN` | O token |
| `IG_TOKEN_GENERATED_AT` | Quando o token foi gerado. O renovador lê isso: token com menos de 24h ele nem tenta renovar (a Meta recusaria) — sai em silêncio e tenta na semana seguinte |
| `IG_VIDEO_HOST_PROVIDER` | `bunny` ou `manual` — seção 6 |
| `IG_SHARE_TO_FEED` | `true` (padrão) faz o Reel aparecer também no feed |

`IG_APP_ID_INSTAGRAM` e `IG_APP_SECRET` aparecem no molde como **opcionais e comentados**: nada no
fluxo do dia a dia lê essas duas. Só faz diferença se um dia você for gerar um token do zero por
fora. Não perca tempo com elas agora.

---

## 6. Hospedar o vídeo — a parte que mais confunde

A Graph API **não recebe o seu arquivo**. Você dá um link, e o servidor da Meta vai lá buscar.

### O contrato técnico **[COMPROVADO]**

Antes de mandar qualquer coisa pra Meta, o próprio script confere o seu link e **reprova** se ele
não passar em todos estes pontos:

1. É `https://` público — **sem login, sem senha, sem "peça acesso"**. Link `http://` (sem o **s**)
   é recusado aqui mesmo, com mensagem clara, em vez de falhar lá na Meta.
2. Responde `HEAD` com **status 200**.
3. O `Content-Type` da resposta contém **`video`** (ex.: `video/mp4`).

Esse guard existe de propósito: é muito melhor falhar em 2 segundos na sua máquina, com mensagem
clara, do que mandar pra Meta e receber de volta um erro genérico 5 minutos depois.

### ⚠️ Por que Google Drive, Dropbox e link de nuvem comum NÃO funcionam

Eles servem uma **página de visualização**, não o arquivo. O `Content-Type` volta como `text/html`
(ou como anexo genérico), e reprova no item 3 acima. **Isso não é bug do produto** — é o link que
não é um link de vídeo. Mesma coisa vale pra GitHub Releases e `raw.githubusercontent`: o conteúdo
volta marcado como anexo/octet-stream em vez de `video/*`, então também reprova.

Se você viu a mensagem "o link não responde como vídeo", é isto. Troque a hospedagem.

### Opção A — Bunny Storage (caminho automatizado)

O script **sobe o MP4 sozinho** e monta a URL. Você não faz nada além de colocar o vídeo na fila.

- Custa **poucos dólares por mês** e **pede cartão** no cadastro. Estamos dizendo isso na cara dura
  porque é a única fricção real dessa opção.
- Você vai precisar de 5 dados do painel do Bunny (o Claude pergunta cada um): zona de storage,
  host de storage, senha/AccessKey da zona, host de pull (o domínio CDN) e a pasta (`reels`).

### Opção B — Modo manual (custo zero)

Você hospeda o vídeo **onde quiser** (qualquer servidor/CDN que passe no contrato acima) e cola a
URL num arquivo ao lado do vídeo. Zero custo, zero cartão — em troca, você cola um link por vídeo.

Funciona assim: pra cada `meu-reel.mp4` na fila, você cria um `meu-reel.url` com a URL dentro.

### Opção C — Cloudflare R2 e afins

Documentado como alternativa avançada, **sem código nesta versão**. Se você já tem um R2, use o
**modo manual**: gere o link público lá e cole no `.url`. Funciona igual.

---

## 7. A fila de vídeos e as legendas

Tudo mora em `~/.operacao-ia/data/social-media/reels-queue/`.

A convenção é 1 vídeo + 1 legenda, mesmo nome:

```
reels-queue/
├── lancamento-01.mp4      ← o vídeo
├── lancamento-01.txt      ← a legenda (OBRIGATÓRIA)
└── lancamento-01.url      ← só no modo manual: a URL pública do vídeo
```

**Sem o `.txt`, o vídeo é pulado** — de propósito, e isso **não é erro**. É a garantia de que nada
vai pro seu perfil com um texto que você não escreveu. O aviso vai pro log
(`~/.operacao-ia/logs/ig-publish.log`) e numa notificação do macOS **mesmo quando outro vídeo foi
publicado com sucesso** — nenhum item some em silêncio. O `--dry-run` também mostra "faltando
legenda" antes de você depender disso.

No **modo manual**, o `.url` é tão obrigatório quanto a legenda: sem ele (ou com um link que não seja
`https://` público) o vídeo entra na mesma lista de pulados, **sem travar a fila**. Um item com
problema nunca segura os outros.

Sobre o tamanho da legenda: acima de **2200 caracteres** o vídeo é pulado. **[ALTA]** — é o limite
que conhecemos hoje; se a Meta tiver mudado, a mensagem te avisa pra conferir na documentação oficial.

Três travas importantes que você não vê, mas que te protegem:

- **1 post por dia**, contado pela hora do **seu** Mac. Se o script rodar duas vezes no mesmo dia,
  o segundo não publica.
- **Identidade pelo conteúdo do arquivo**, não pelo nome. Renomear um vídeo já postado **não** faz
  ele ser postado de novo. Por isso mesmo, um arquivo que acabou de ser copiado pra pasta (menos de
  60 segundos) espera a próxima execução: hashear um vídeo pela metade faria ele ser publicado duas vezes.
- **Se o registro do que já foi postado estiver corrompido, o script não publica nada.** Prefere
  parar e te avisar a arriscar republicar a fila inteira (seção 11).

---

## 8. Testar antes de confiar (`--dry-run`)

`--dry-run` é o modo "me mostra o que você faria, mas não faça". **Nenhuma chamada à API acontece.**

Peça pro Claude: *"roda o dry-run da publicação do Instagram"*. Ele executa
`python3 automations/instagram/instagram_reel_daily.py --dry-run` e te mostra:

- qual vídeo seria publicado agora,
- quantos ainda estão na fila,
- a legenda exata que iria junto,
- a URL pública que seria usada.

Existe também `--check`, que só valida a credencial (não olha a fila, não publica nada).

**Leia a legenda com atenção nesse momento.** É o seu perfil.

---

## 9. Agendar

Só depois que o dry-run te convencer, o Claude pergunta se pode agendar — e você responde
explicitamente. São dois agendamentos (LaunchAgent, o agendador nativo do macOS):

| Agendamento | O que faz | Quando |
|---|---|---|
| `com.socialmediaagent.ig-reel-daily` | publica 1 Reel | todo dia, no horário que você escolher |
| `com.socialmediaagent.ig-token-refresh` | renova o token | 1x por semana |

Pra conferir depois se continuam ativos, o comando é:

```
launchctl list | grep socialmediaagent
```

Duas linhas = tudo certo. Nenhuma linha = o agendamento sumiu (acontece em migração de Mac) —
peça pro Claude reinstalar com `python3 setup/setup_publicacao_ig.py`.

Se só **um** dos dois subir, a configuração te diz **qual** ficou ativo e qual não — ela nunca diz
"não ativei" com a publicação diária ligada. E se a publicação subir sem a renovação do token, ela
oferece desligar a publicação, porque publicar sem renovar significa parar de funcionar em 60 dias.

Pra desligar tudo: `python3 setup/setup_publicacao_ig.py --uninstall`. Isso remove os dois
agendamentos e **não apaga** o seu `instagram.env`.

> **Só macOS nesta versão.** Em Windows ou Linux o bônus até roda no modo manual (você dispara
> quando quiser), mas não instala agendamento — preferimos avisar a fingir um suporte que não
> testamos.

---

## 10. Manter o token vivo

O agendamento semanal cuida disso sozinho: ele chama o endpoint de renovação, **faz backup do
arquivo de configuração antes de sobrescrever** (mantendo as 12 cópias mais recentes) e grava o
token novo — e **confere, relendo o arquivo, que o token gravado é mesmo o novo**. Se não conseguir
gravar, ele te avisa; nunca diz "renovado" sem ter renovado de verdade.

Se o token tiver **menos de 24 horas**, ele nem tenta (a Meta recusaria) e avisa que renova na semana
seguinte. Isso não é erro: é o que acontece com quem configura o bônus num domingo à noite.

Você só precisa saber de uma coisa: **Mac desligado por semanas seguidas = renovação não roda =
token expira em 60 dias.** Se voltar depois disso, refaça o passo 3.4 e gere um token novo.

Log de tudo: `~/.operacao-ia/logs/`.

---

## 11. Erros comuns — causa e o que fazer

### `400 IGApiException code 100: The parameter access_token is required` na renovação **[COMPROVADO]**
**Causa:** o token foi enviado no cabeçalho da requisição em vez de ir na URL. O endpoint de
renovação do Instagram é o único que **ignora** `Authorization: Bearer` e exige o token como
parâmetro na própria URL.
**O que fazer:** nada — o código já está do jeito certo, com comentário avisando pra ninguém
"consertar" e quebrar de novo. Se você viu esse erro, alguém editou o script. Restaure o original.

### "Abortado por rate limit" / `X-App-Usage` **[COMPROVADO]**
**Causa:** o seu App passou de 90% da cota de chamadas da Meta na janela atual. O script **para de
propósito**, antes que a Meta bloqueie o App.
**O que fazer:** esperar a janela virar. Se acontece direto e você posta 1 Reel/dia, algo está
chamando a API em loop — chame o suporte.

### "O Instagram recusou o vídeo" / container `ERROR` ou `EXPIRED` **[ALTA]**
**Causa:** o servidor da Meta não conseguiu processar o vídeo. Quase sempre é (a) a URL não estava
publicamente acessível pra ele, (b) o vídeo estava fora das especificações de Reels.
**Isso não é uma publicação incerta.** Quando a Meta recusa, ela recusa com todas as letras: **nada
foi publicado**, o script te diz o motivo na tela e **libera o arquivo** — depois que você corrigir o
vídeo (ou o link), ele volta a ser publicado normalmente, sem você precisar de nenhum comando.
**O que fazer:** abra a URL do vídeo numa **janela anônima** do navegador — se pedir login ou não
tocar, é a causa (a). Se abrir normal, confira duração/proporção/codec na
[documentação oficial de Reels da Meta](https://developers.facebook.com/docs/instagram-platform).
Não fixamos números aqui de propósito: a Meta muda as specs e um número errado neste guia seria pior
que nenhum número.

### `The media couldn't be fetched` **[ALTA]**
Mesma causa do item acima: a Meta não conseguiu baixar o seu vídeo. Comece pelo teste da janela
anônima.

### `error code 190` **[ALTA]**
**Causa:** token inválido, revogado ou expirado.
**O que fazer:** se faz menos de 60 dias, rode a renovação. Se faz mais, gere um token novo
(passo 3.4). Se você trocou a senha do Instagram ou removeu o App recentemente, o token também morre.

### "Permissão negada" mesmo com as duas permissões aprovadas **[VERIFICAR]**
**Causa provável:** o App está em *Development Mode* e a sua conta do Instagram não foi adicionada
como **tester** dentro dele (passo 3.7).
**O que fazer:** adicione a conta como tester no painel do App e aceite o convite pelo Instagram.

### "O link não responde como vídeo" / reprovou antes de publicar **[COMPROVADO]**
**Causa:** o guard da seção 6 barrou a URL — ela não é pública, não devolveu 200, ou não tem
`Content-Type` de vídeo.
**O que fazer:** troque a hospedagem. Drive/Dropbox/GitHub não servem (seção 6).

### "Publish ambíguo — não repostei automaticamente" **[COMPROVADO]**
**Causa:** o vídeo foi enviado, o container foi criado, mas a confirmação final de publicação não
chegou (queda de rede, timeout). O script **não sabe** se o post saiu ou não.
**O que fazer:** **abra o seu Instagram e olhe.**
- Se o Reel **está** lá: nada a fazer. Ele fica marcado e não será republicado.
- Se **não** está: **diga isso pro Claude no chat** ("conferi, o Reel não está no meu perfil"). Só
  depois dessa sua confirmação ele roda
  `python3 automations/instagram/instagram_reel_daily.py --retry-ambiguous nome-do-arquivo.mp4 --confirmo-que-nao-foi-publicado`.
  Essa flag **é** a sua confirmação: sem ela o script se recusa a republicar. Se você mesmo rodar o
  comando no terminal, sem a flag, ele pede a confirmação digitada na hora.

> **Por que não retentamos sozinhos:** o pior resultado possível aqui é o **mesmo Reel publicado
> duas vezes no seu perfil**, na frente da sua audiência. Preferimos te dar 30 segundos de trabalho
> manual a arriscar isso. É uma decisão de projeto, não uma falta.

### "Não vou publicar — o controle de posts está corrompido" **[COMPROVADO]**
**Causa:** o arquivo que guarda o que já foi postado
(`~/.operacao-ia/data/social-media/ig-publish-state.json`) existe mas não pôde ser lido. Acontece com
desligamento no botão durante a execução, restauração de backup pela metade ou edição manual.
**O que o script faz:** **para, e não publica nada.** Sem esse registro ele não sabe o que já foi ao
ar — e recomeçar do zero republicaria a fila inteira, um vídeo duplicado por dia.
**O que fazer:** primeiro **tire da fila os vídeos que você já publicou**. Só então peça pro Claude
rodar `python3 automations/instagram/instagram_reel_daily.py --recomecar-controle` — ele guarda o
arquivo velho com a data no nome e recomeça o histórico.

### Rodou e não aconteceu nada, sem erro
Provavelmente é um destes três, todos normais: fila vazia, já houve post hoje, ou nenhum vídeo tem
legenda `.txt`. O log em `~/.operacao-ia/logs/ig-publish.log` registra qual foi — inclusive a lista
dos itens pulados e o motivo de cada um.

---

## 12. Limitações — ditas na cara dura

- **Precisa do Mac ligado e acordado** no horário. Não há servidor no meio.
- **Mac muito tempo desligado** → renovação semanal não roda → token expira em 60 dias.
- **1 conta do Instagram** por instalação.
- **Só Reels.** Nada de Stories, Feed de foto ou Carrossel.
- **Agendamento só no macOS** nesta versão.
- **A Meta tem um teto diário de publicações via API.** Existe, é baixo o suficiente pra não
  atrapalhar quem posta 1/dia, e o número vigente está na
  [documentação oficial](https://developers.facebook.com/docs/instagram-platform) — não fixamos aqui
  porque ele muda.
- **Não existe alarme automático** se o agendamento sumir. A conferência é o comando da seção 9.
- **O token fica em texto plano** no seu Mac (seção 5).

---

## 13. Resumo pra quem só quer começar

1. Converta a conta pra **Business ou Creator**.
2. Peça pro Claude: **"quero ativar a publicação automática no Instagram"**.
3. Ele te guia até o token, valida ao vivo, **mostra o @ conectado pra você confirmar que é a sua
   conta**, e roda um teste sem publicar.
4. Você olha o teste. Gostou → autoriza o agendamento.
5. Daí em diante: joga `video.mp4` + `video.txt` na fila e segue a vida.

Se travar em qualquer ponto, mostre a mensagem de erro pro Claude — ele conhece este documento
inteiro e resolve com você.
