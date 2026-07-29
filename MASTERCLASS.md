# MasterClass Setup 7 — Roteiro do Vídeo

Vídeo único (aula MasterClass) que apresenta todo o Setup. Será hospedado no Bunny e exibido em `panel-s7-0` da área de membros do ZX Control.

**Duração-alvo:** 12-18 minutos.

## Estrutura

### 1. Abertura (0:00 - 1:30)
- Contexto: aluno já tem agente de tráfego (Setup 6) → agora precisa alimentar funil orgânico
- Promessa: ao final, criar Reel + carrossel + thumb sem editor de vídeo, sem designer, sem ficar travado em frente à tela em branco
- Princípio: Setup 7 é sobre CRIAR — a publicação é manual por padrão (você decide quando e onde postar). Pro Instagram existe um bônus opcional: publicação automática de 1 Reel por dia via token Meta. O passo a passo completo está em `docs/PUBLICACAO-AUTOMATICA-INSTAGRAM.md`; o vídeo de apresentação do Setup de Tráfego Pago entra como apoio pra quem nunca mexeu no Meta for Developers.

### 2. Quem deve usar (1:30 - 2:30)
- Criador solo / personal brand
- Quem tem 4 plataformas pra alimentar e não tem tempo
- Quem quer manter consistência visual sem virar designer

### 3. Demo ao vivo (2:30 - 9:00)
Mostrar 3 comandos em sequência:

- `criar reel sobre [tema do nicho do criador]` — Reel animado em MP4 (HTML → Chrome → ffmpeg), 100% local. Mostrar como roda sem mexer no After Effects.
- `gerar carrossel 7 slides sobre [tema] para linkedin` — copy do Claude + imagens via `gerar-imagem` (gpt-image-2 com ChatGPT Plus, fallback Gemini)
- `thumb yt: [título]` — 3 variantes via `gerar-imagem`

Comentar enquanto roda: como o `DESIGN.md` mantém consistência, como o `marca.json` define a voz, custo zero do Reel animado (renderiza local), e custo praticamente zero das imagens (gpt-image-2 usa a assinatura ChatGPT que o aluno provavelmente já tem).

### 4. Workflow semanal sugerido (9:00 - 12:00)
- Cadência 3-2-1: 3 Reels + 2 carrosséis + 1 longo (YouTube)
- Stories diárias usando o pack semanal
- Repurpose 1x por mês de uma live longa

### 5. Setup explicado em alto nível (12:00 - 15:00)
- 8 etapas, ~30min total
- Bônus opcional, fora das 8 etapas: publicação automática de 1 Reel/dia no Instagram (integração com token Instagram/Meta)
- O que cada etapa configura
- Pré-requisitos:
  - **Base:** Setups 1-6, Python 3.10+, `gh` CLI, `ffmpeg` (`brew install ffmpeg`), Claude Code instalado
  - **Reels:** Chrome ou Chromium + **Bun** (`brew install bun`) para o pipeline puppeteer + ffmpeg
  - **Imagens:** 1 provider — ChatGPT Plus com Codex CLI (recomendado pra gpt-image-2) **OU** chave Gemini grátis em `~/.operacao-ia/config/gemini.env`. Higgsfield é opcional/não usado pelo gateway.
  - **Transcrição** (opcional, melhora muito o repurpose): chave ElevenLabs Scribe; Whisper local cobre como fallback.

### 6. Custos & expectativas (15:00 - 17:00)
- **Reels em MP4 = grátis** (renderiza local, sem créditos AI)
- **Imagens (carrossel/thumb) = grátis ou quase** se o aluno usa gpt-image-2 via ChatGPT Plus, ou Gemini free tier
- **Transcrição de live = grátis** com ElevenLabs free tier (minutos incluídos variam por plano — ver pricing oficial), ou 100% offline com Whisper local
- Higgsfield NÃO entra como provider de imagem (só image2/gemini/imagen); Higgsfield video só pra quem já tem plano pago
- Tempo de geração realista: Reel 30s leva ~5-15s; carrossel 7 slides ~30-60s; transcrição de 1h ~3min (ElevenLabs) ou ~20-40min (Whisper)

### 7. CTA (17:00 - 18:00)
- Instalar agora
- Próximos setups
- Comunidade

## Notas de produção

- Gravar com fundo `DESIGN.md dark-mono` pra demonstrar o sistema
- Mostrar a tela do Claude Code com font legível (zoom in)
- Banner ZX LAB sutil no canto superior direito (consistente com cortes-masterclass)
- Áudio limpo: cadeia `acompressor` + `highshelf` + `loudnorm` no ffmpeg

## Publicação

Depois de gravado, o vídeo é hospedado e o player entra em `panel-s7-0` da área de
membros, no lugar do placeholder `BUNNY_GUID_S7`. O passo a passo de publicação é
operacional da ZX LAB e não faz parte deste repositório.
