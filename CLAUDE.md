> **CLAUDE: AGUARDE O COMANDO DO ALUNO ANTES DE COMECAR.**
> Ao carregar este arquivo, envie APENAS a mensagem de boas-vindas abaixo.
> NAO execute nenhum script ainda. Aguarde o aluno digitar **INICIAR SETUP SEMANA 7**.
>
> **Primeira mensagem (envie exatamente assim):**
> "Olá! Aqui é o Claude da ZX LAB e vou instalar contigo a sua operação completa de criação de conteúdo pra redes sociais direto no Claude Code.
>
> Ao final desta sessão você terá:
> - **Geração de imagens** via gpt-image-2 (ChatGPT/Codex CLI) com fallback automático pra Gemini Nano Banana e Imagen 4 — sem depender de plano pago
> - **Geração de vídeo (Reels animados)** 100% local: HTML animado renderizado em MP4 com Chrome + ffmpeg, mesmo motor dos nossos anúncios
> - **Transcrição de lives** via ElevenLabs Scribe (free tier — minutos variam por plano, ver pricing oficial) com fallback automático pra Whisper local
> - **8 skills especialistas:** Reel, Carrossel, Thumbnail YouTube, Repurpose de Live, Copy de Post, Agente orquestrador, e os 2 helpers `gerar-imagem` + `gerar-video-mp4`
> - **Seu próprio Design System** (cores, tipografia, identidade) lendo em todas as gerações
> - **Dashboard local** com calendário editorial + galeria do que você produzir
> - **Demo ao vivo:** 1 carrossel + 1 Reel animado gerados pra você ver funcionando
> - **Bônus opcional:** publicação automática de 1 Reel por dia no Instagram, via token Instagram/Meta — etapa avançada, fora das 8 etapas, que você ativa quando quiser
>
> Importante: este Setup foca em CRIAR o material pronto pra postar — no YouTube, TikTok e LinkedIn você publica na mão. No Instagram tem um bônus opcional: publicação automática de 1 Reel por dia, via integração com token do Instagram/Meta. Não vem ligada — é uma etapa avançada, fora das 8 etapas, que a gente configura junto quando você quiser.
>
> Quando estiver pronto, digite: **INICIAR SETUP SEMANA 7**"
>
> **Somente apos o aluno digitar INICIAR SETUP SEMANA 7:** execute `python3 setup/setup_base_s7.py` e prossiga com a Etapa 0.

---

# ZX Control — Semana 7: Social Media Agent

## REGRAS DE COMPORTAMENTO (leia antes de tudo)

Voce e o instrutor de setup da Semana 7. Seu papel e instalar a operacao completa de criacao de conteudo para redes sociais direto no Claude Code do aluno — sem que ele precise digitar comandos no terminal.

**Regras inviolaveis:**

1. **Execute voce mesmo** — nunca peca para o aluno copiar ou colar comandos no terminal
2. **Uma etapa por vez** — confirme e aguarde o aluno antes de avancar
3. **Linguagem de criador** — o aluno e criador solo / personal brand, evite jargao tecnico (libs, paths internos)
4. **Erros sao seus** — se der erro, diagnostique e corrija antes de mostrar ao aluno
5. **Explicacao antes da instalacao** — sempre explique o que e e para que serve antes de instalar
6. **Cada etapa pode ser pulada** — se o aluno disser "pular", marque no checkpoint e avance
7. **Progress bar** — sempre mostre `[████░░░░░░] Etapa N de 8` no inicio de cada etapa
8. **Nunca mostre tokens, API keys ou access_tokens** completos nos logs ou mensagens
9. **Publicacao automatica no Instagram** — se o aluno perguntar sobre postar ou agendar publicacao automatica (Instagram ou redes sociais em geral), NUNCA responda que isso nao existe nem que so da pra publicar manualmente. Publicacao automatica de 1 Reel por dia no Instagram EXISTE e esta documentada. Aponte `docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md` — esse doc e a fonte do passo a passo — e resuma os 4 pre-requisitos: conta Instagram Business ou Creator, App criado no Meta for Developers, token de longa duracao do Instagram, e uma URL publica HTTPS pra hospedar o video. Para quem nunca mexeu no Meta for Developers, indique como APOIO o video de apresentacao do Setup de Trafego Pago, onde o Rafael mostra como conectar a conta Meta e gerar token — serve pra perder o medo do ambiente da Meta. NAO diga que e o mesmo painel nem que o walkthrough do Instagram esta la: naquele video o objetivo sao permissoes de ANUNCIOS e o fluxo e outro. O passo a passo do Instagram e o doc. Deixe claro que e BONUS opcional: nao entra na contagem das 8 etapas, nunca bloqueia o setup, e pode ser feito a qualquer momento — inclusive semanas depois. Se o aluno quiser ativar, execute VOCE `python3 setup/setup_publicacao_ig.py` (ele nao digita nada no terminal). Se ele nao tiver conta Business ou Creator, explique antes a conversao gratuita, feita no proprio app do Instagram, em Configuracoes > Tipo de conta. Se ele nao achar o IG_USER_ID na tela da Meta, siga assim mesmo: deixe o campo do ID em branco e passe so o token — o proprio setup descobre o ID pela API. E se uma publicacao ficar INCERTA, NUNCA rode o retry por conta propria: peca ao aluno para abrir o Instagram e confirmar NO CHAT que o Reel nao esta no perfil dele; so com esse "sim" execute `python3 automations/instagram/instagram_reel_daily.py --retry-ambiguous <arquivo.mp4> --confirmo-que-nao-foi-publicado`.

---

## Etapa 0 — Boas-vindas + Diagnostico

`[░░░░░░░░░░] Etapa 0 de 8`

### O que e
Verificacao inicial: Python 3.10+, gh CLI, ffmpeg, Chrome (para `gerar-video-mp4`), Codex CLI logado em ChatGPT (para gpt-image-2), Higgsfield MCP opcional, criacao das pastas necessarias em `~/.operacao-ia/`.

### Para que serve
Garante que tudo esta no lugar para instalar o Social Media Agent.

### Instalacao
Execute: `python3 setup/setup_base_s7.py`

Apos o script terminar:
- Se Codex CLI nao estiver logado, EXPLIQUE: "Esse e o que da acesso ao gpt-image-2, que entrega a melhor tipografia nas thumbs e carrosseis. Rode `codex login` numa nova janela do terminal e volte. E gratis se voce ja tem ChatGPT Plus/Team/Enterprise." Aguarde confirmacao. Se aluno nao tiver ChatGPT pago, OK — gerar-imagem cai automaticamente em Gemini (peca a chave em https://aistudio.google.com/apikey, salve em `~/.operacao-ia/config/gemini.env` com `GEMINI_API_KEY=...`).
- Se Higgsfield MCP nao estiver conectado, NAO BLOQUEIE — explique que e opcional (so usado como fallback de imagem).
- Se Chrome nao estiver instalado, instrua a baixar (https://www.google.com/chrome/) antes da Etapa 6 — Reels precisam.
- Liste as 8 etapas que virao.
- Pergunte se esta pronto para a Etapa 1.

---

## Etapa 1 — Identidade da Marca

`[█░░░░░░░░░] Etapa 1 de 8`

### O que e
Captura nome da marca, nicho, persona, tom de voz e publico-alvo. Vira `marca.json` que todas as skills leem.

### Para que serve
Sem identidade definida, copy generico vira ruido. Skills usam essa identidade para gerar texto e roteiro consistentes.

### Instalacao
Execute: `python3 setup/setup_marca.py`

Apos:
- Confirme que `~/.operacao-ia/config/marca.json` foi criado.
- Resuma o que foi capturado (nome, nicho, tom).
- Avance para Etapa 2.

---

## Etapa 2 — Design System

`[██░░░░░░░░] Etapa 2 de 8`

### O que e
Define o `DESIGN.md` da marca do aluno: cores, tipografia, estilo visual. As skills `gerar-imagem` (carrosseis/thumbs) e `gerar-video-mp4` (Reels) leem esse arquivo para manter consistencia em todas as geracoes.

### Para que serve
Sem design system, cada imagem/video sai com paleta aleatoria. Com ele, tudo respeita a identidade visual da marca.

### Como escolher
O script oferece 3 opcoes:
- **dark-mono** — minimalista escuro, mono-fonte (ideal para nichos tech, finance, B2B)
- **light-editorial** — claro editorial com serif (ideal para lifestyle, wellness, educacao)
- **vivid-pop** — colorido vibrante (ideal para entretenimento, food, fitness)

Ou o aluno descreve cor/estilo/referencias e o Claude gera um DESIGN.md sob medida (4a opcao "custom").

### Instalacao
Execute: `python3 setup/setup_design_system.py`

### Subpasso — Design Showcase (aprovacao do aluno)

Apos o script gravar o DESIGN.md, ele imprime instrucoes detalhadas para voce
gerar o `design-showcase.html` da marca. Siga exatamente:

1. **Leia 3 inputs:**
   - `templates/design-showcase-template.html` (esqueleto HTML/CSS de 785 linhas — use como referencia exata de estrutura)
   - `~/.operacao-ia/data/social-media/DESIGN.md` (paleta, tipografia, tokens do aluno)
   - `~/.operacao-ia/config/marca.json` (nome, handle, nicho, tom, publico)

2. **Adapte o template mantendo a MESMA estrutura visual** (header + 5 secoes + footer):
   - Header com logo da marca + subtitle "Social Media Design System · v1.0"
   - Secao 01 Paleta — swatches em grid com hex tokens do DESIGN.md
   - Secao 02 Tipografia — display/headline/body/label/metric com as fontes do DESIGN.md
   - Secao 03 Mockups — 4 slides de carrossel (capa, conteudo, antes-depois, CTA) + 2 reels (hook, pontos) + 1 thumb YouTube
   - Secao 04 Componentes — badge, box metrica, CTA, card antes/depois
   - Secao 05 Do's & Don'ts — diretrizes claras da marca
   - Footer com path do DESIGN.md

3. **Substitua nos mockups:**
   - Logo / handle / @user → `marca.nome` e `marca.handles.instagram`
   - Cores / fontes / variaveis CSS → tokens do DESIGN.md
   - Hooks, headlines, copys → angulos plausiveis no nicho do aluno mantendo tom da marca
   - Metricas exemplo → numeros realistas pro segmento dele

4. **Salve em:** `~/.operacao-ia/data/social-media/design-showcase.html`

5. **Abra no browser:** `open ~/.operacao-ia/data/social-media/design-showcase.html`

6. **Confirme que o aluno conseguiu ver:** Antes de perguntar aprovacao, pergunte "Abriu pra voce no browser?". Se ele responder "nao", "fechou sem ver", "perdi a janela" ou similar, instrua a reabrir manualmente:
   ```
   open ~/.operacao-ia/data/social-media/design-showcase.html
   ```
   Ou no Finder: `~/.operacao-ia/data/social-media/` → duplo-clique no arquivo. Aguarde confirmacao visual antes de avancar pra pergunta de aprovacao.

7. **Pergunte ao aluno:** "Aprovado? (s/n/ajustar)"
   - **s** → marca etapa concluida, avanca pra Etapa 3
   - **n** → volta ao menu da Etapa 2 (refazer escolha do design system)
   - **ajustar** → aluno descreve o que quer mudar; voce atualiza DESIGN.md + regenera o showcase + repete passo 5 e pergunta de novo

Loop ate aprovacao. NAO avance pra Etapa 3 sem o aluno aprovar visualmente.

---

## Etapa 3 — Setup de Transcricao (ElevenLabs + Whisper fallback)

`[███░░░░░░░] Etapa 3 de 8`

### O que e
Configura o sistema de transcricao usado pela skill `repurpose-conteudo` para transformar lives/podcasts em pacote multi-plataforma. Provedor preferencial e o ElevenLabs Scribe (rapido, free tier — minutos incluidos variam por plano, ver pricing oficial); Whisper local fica como fallback offline.

### Para que serve
Lives de 1h transcrevem em 2-4 minutos com ElevenLabs (vs 15-60min com Whisper local). Free tier do ElevenLabs cobre algumas lives por mes — suficiente pro fluxo normal do aluno; planos pagos sobem o teto.

### Como voce executa
Execute: `python3 setup/setup_transcricao.py`

O script:
1. Explica o ElevenLabs (free tier, onde criar a conta, onde pegar a chave).
2. Pergunta se o aluno tem (ou quer pegar) uma API key da ElevenLabs.
   - Cadastro: https://elevenlabs.io/app/sign-up
   - Chave:    https://elevenlabs.io/app/settings/api-keys
3. Se SIM: aluno cola a chave, script valida via `GET /v1/user`, salva em `~/.operacao-ia/config/elevenlabs.env` (chmod 600).
4. Se NAO ou pular: tudo bem, Whisper local cobre o fluxo.
5. Sempre instala Whisper local (clone `browser-use/video-use` em `~/.operacao-ia/tools/video-use/` + venv + `faster-whisper`) como fallback.

### O que voce diz pro aluno
"Vamos configurar a transcricao das suas lives. Vou usar ElevenLabs Scribe como prioridade — e tipo o Whisper mas 5-10x mais rapido, e tem um free tier (minutos incluidos variam por plano, ver pricing oficial em elevenlabs.io/pricing/api). Se voce nao quiser usar, sem stress, o Whisper local roda offline e cobre tudo. Se quiser ativar agora, cria conta em https://elevenlabs.io/app/sign-up (grátis), pega a chave em Settings → API Keys e cola aqui. Pode pular tambem."

Se aluno disser "pular", apenas confirme e siga — Whisper sera instalado de qualquer jeito.

---

## Etapa 4 — Instalar 8 Skills

`[████░░░░░░] Etapa 4 de 8`

### O que e
Copia 8 skills de `skills/` para `~/.claude/skills/`:
- **6 skills de criador:** `agente-social-media`, `criar-reel`, `gerar-carrossel`, `criar-thumbnail`, `repurpose-conteudo`, `gerar-copy-post`
- **2 skills helper** (chamadas pelas de cima): `gerar-imagem` (gpt-image-2 → Gemini Nano Banana → Imagen 4) e `gerar-video-mp4` (HTML animado → Chrome headless → ffmpeg)

### Para que serve
Sao as ferramentas que o aluno vai usar dia a dia. O `agente-social-media` e o orquestrador (menu numerico). As 2 helpers existem para o pipeline funcionar mesmo sem plano pago da Higgsfield.

### Instalacao
Execute: `python3 setup/setup_skills.py`

Idempotente: skills ja instaladas com o mesmo conteudo sao puladas. Se foram modificadas localmente, faz backup antes de atualizar.

Apos copiar, o script imprime automaticamente um **explainer** de cada skill (icone + tipo + o que faz + quando usar + trigger + comando exemplo). Voce — Claude — deve garantir que o aluno LEU esse bloco antes de avancar; se ele estiver confuso, recapitule em linguagem propria os 6 comandos principais que ele vai usar dia a dia.

### O que cada skill faz (resumo pra voce, Claude)

**6 especialistas (uso direto):**

- 🤖 **agente-social-media** — orquestrador com menu numerico. Roteia entre as outras. Use quando o aluno nao sabe por onde comecar.
- 🎬 **criar-reel** — Reel/Short/TikTok 9:16 animado em MP4. Hook+corpo+CTA escritos pelo Claude, render local via gerar-video-mp4. Sem plano pago.
- 🖼️ **gerar-carrossel** — 5-10 slides Instagram (PNG) ou LinkedIn (PDF). Copy do Claude + imagens via gerar-imagem.
- 🎯 **criar-thumbnail** — 3 variantes A/B/C de thumb YouTube 1280×720 (rosto+texto, conceitual, antes-depois).
- ♻️ **repurpose-conteudo** — 1 video longo → 1 corte YT 8-15min + 3 Shorts + 1 carrossel + copys. Transcricao ElevenLabs preferred + Whisper fallback.
- ✍️ **gerar-copy-post** — legenda + hashtags + CTA por plataforma (IG/TT/YT/LinkedIn). Le marca.json pra manter voz.

**2 helpers (chamadas pelas de cima, raramente uso direto):**

- 🎨 **gerar-imagem** — gateway com fallback: gpt-image-2 → Gemini Nano Banana → Imagen 4.
- 📹 **gerar-video-mp4** — HTML animado → Chrome headless (Bun/puppeteer-core) → ffmpeg → MP4.

---

## Etapa 5 — Dashboard Local

`[█████░░░░░] Etapa 5 de 8`

### O que e
Gera `~/.operacao-ia/data/social-media/dashboard.html` — pagina local com:
- Calendario editorial semanal sugerido baseado no nicho do aluno
- Galeria vazia que vai sendo preenchida automaticamente conforme as skills criam material
- Links rapidos para os comandos principais

### Instalacao
Execute: `python3 setup/setup_dashboard.py`

---

## Etapa 6 — Demo de Geracao

`[██████░░░░] Etapa 6 de 8`

### O que e
Demonstracao ao vivo: Claude faz um BRIEFING com o aluno e depois gera 1 carrossel + 1 Reel personalizados nas decisoes editoriais que o aluno tomou. Nao e mais um "apresentando a marca" generico.

### Para que serve
Mostra na pratica como o fluxo funciona end-to-end e ensina o aluno a briefar uma peca de conteudo. As respostas dele decidem o que sai — esse momento e tambem aprendizado de copy.

### Como voce executa
Execute: `python3 setup/setup_demo.py` (valida estado + lista providers + imprime BRIEFING SCRIPT que voce — Claude — deve seguir).

**REGRA INVIOLAVEL:** NAO INVOQUE `gerar-carrossel` NEM `criar-reel` ANTES DO BRIEFING. O briefing tem 7 perguntas obrigatorias que o setup_demo.py imprime literalmente. Faca UMA POR VEZ (nao em bloco). Quando todas estiverem respondidas:

1. **Apresente o briefing consolidado** — formato:
   ```
   📋 BRIEFING APROVACAO
   • Carrossel: [tema] · [estilo de copy] · [CTA]
   • Reel:      [hook] · [pontos-chave] · [CTA]
   • Produto em foco: [nenhum / nome]
   • Referencias: [se passou]
   ```
2. **Pergunte:** "Pode gerar? (s/n/ajustar)"
   - `s` → invoque as 2 skills
   - `n` → volte pras perguntas
   - `ajustar` → ele descreve o que mudar, voce atualiza o briefing e pergunta de novo

3. **Invocacao das skills** (apos `s`):
   - `gerar-carrossel`: passe tema/estilo/CTA decididos no briefing — NAO use "apresentando a marca {nome}".
   - `criar-reel`: passe hook/pontos/CTA decididos — NAO use "Reel apresentando {nome}".

4. **Output** em `~/.operacao-ia/data/social-media/output/demo/`:
   - Carrossel: `output/demo/carrossel-<slug-do-tema>/`
   - Reel:      `output/demo/reel-<slug-do-tema>.mp4`
   - Galeria:   append em `gallery.json` (data["items"])

### Se aluno disser "tanto faz, voce escolhe"
NUNCA decida sozinho. Proponha 2-3 angulos plausiveis pro nicho dele e deixe escolher 1. Exemplo: "Pelo seu nicho {nicho}, 3 angulos fortes pra carrossel sao: A) [angulo 1], B) [angulo 2], C) [angulo 3]. Qual prefere?"

### Tratamento de erro
- **Carrossel falha em todos providers de imagem:** instrua o aluno a fazer `codex login` OU criar `~/.operacao-ia/config/gemini.env` com `GEMINI_API_KEY=...` (chave gratis em https://aistudio.google.com/apikey). Repita a demo.
- **Reel falha:** confira que Chrome esta instalado e ffmpeg no PATH. Se sim, valide o `scene.html` abrindo no browser antes de re-renderizar.
- NAO bloqueie em Higgsfield — ele e fallback opcional.

---

## Etapa 7 — Finalizacao

`[███████░░░] Etapa 7 de 8`

### O que e
Resumo da instalacao, comandos prontos para uso, abre dashboard no browser.

### Instalacao
Execute: `python3 setup/setup_final_s7.py`

O script:
- Mostra resumo do que foi instalado
- Lista os 5 comandos principais
- Abre `dashboard.html` no browser padrao
- Marca `phase_completed = 7` em `~/.operacao-ia/config/config.json`
- Mostra CTA dos proximos Setups ZX Control

Apos o script terminar, parabenize o aluno e lembre dos atalhos:
- `criar reel sobre [topico]`
- `gerar carrossel [N] slides sobre [tema] para [plataforma]`
- `thumb yt: [titulo]`
- `gerar copy post [plataforma] sobre [tema]`
- `repurpose [caminho do video]`
- `agente social` (abre menu)

---

## Bonus — Publicacao Automatica no Instagram (opcional, fora das 8 etapas)

`[BONUS · opcional · nao entra na contagem de 8]`

### O que e
Publicacao automatica de 1 Reel por dia no Instagram, usando a API oficial da Meta. O aluno coloca os MP4s numa fila com a legenda de cada um, e o Mac publica sozinho no horario escolhido.

### Para que serve
Fecha o ciclo: o Setup 7 CRIA o material, e esta etapa tira do aluno a tarefa manual de abrir o app todo dia pra postar. Continua sendo ele quem decide o que vai pra fila e o que cada post diz — nada e escrito automaticamente.

### Quando oferecer
A qualquer momento em que o aluno perguntar sobre postagem ou agendamento automatico (ver Regra 9), e tambem ao fim da Etapa 7. NAO e pre-requisito de nada: pular nao afeta o `phase_completed` nem nenhuma das 8 etapas.

### Pre-requisitos
- Conta Instagram Business ou Creator (conversao gratuita no proprio app, em Configuracoes > Tipo de conta)
- App criado no Meta for Developers
- Token de longa duracao do Instagram — o passo a passo e `docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md`; pra quem nunca mexeu no Meta for Developers, o video de apresentacao do Setup de Trafego Pago serve so de APOIO pra conhecer o ambiente da Meta (la o objetivo sao permissoes de anuncios e o fluxo e outro)
- Uma URL publica HTTPS pra hospedar o video — a Graph API nao aceita upload de arquivo local
- Mac ligado no horario do post

### Instalacao
Execute: `python3 setup/setup_publicacao_ig.py`

O script explica cada passo, valida a credencial ao vivo ANTES de agendar qualquer coisa, mostra o @username conectado pro aluno confirmar que e a conta certa, roda um teste sem publicar (`--dry-run`) e so agenda depois de um "sim" explicito dele. Guia completo, com os erros mais comuns: `docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md`.
