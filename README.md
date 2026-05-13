# Social Media Agent — ZX Control Semana 7

Pacote de criação de conteúdo para redes sociais que roda direto no Claude Code do aluno.

## O que está incluído

**6 skills de criador:**
- `criar-reel` — Reels/Shorts/TikToks animados em MP4 (HTML → Chrome headless → ffmpeg, 100% local)
- `gerar-carrossel` — Carrosséis Instagram/LinkedIn com imagens AI + copy (Claude)
- `criar-thumbnail` — 3 variantes de thumb YouTube (1280×720)
- `repurpose-conteudo` — Live de 1h → corte longo + Reels + carrossel + copys (ElevenLabs Scribe ou Whisper local)
- `gerar-copy-post` — Legenda + hashtags + CTA por plataforma (Claude)
- `agente-social-media` — Orquestrador com menu numérico

**2 skills helper** (chamadas pelas de cima — instaladas no mesmo Setup):
- `gerar-imagem` — gateway de geração de imagem: gpt-image-2 (Codex CLI/ChatGPT) → Gemini Nano Banana → Imagen 4
- `gerar-video-mp4` — pipeline HTML animado → Chrome headless → ffmpeg para renderizar MP4 vertical/horizontal

**3 design systems prontos** + opção de gerar customizado: `dark-mono`, `light-editorial`, `vivid-pop`.

**Dashboard local** com calendário editorial e galeria do que você produz.

## Como instalar

```bash
gh repo clone zxmarketingdigital/social-media-agent ~/social-media-agent
cd ~/social-media-agent
claude
```

Quando o Claude carregar, digite: **INICIAR SETUP SEMANA 7**.

O Claude conduz a instalação completa em 8 etapas (~30min total).

## Pré-requisitos

- Setup 1 a 6 do ZX Control concluídos (`~/.operacao-ia/config/config.json` com `phase_completed >= 6`)
- Python 3.10+
- gh CLI
- ffmpeg (`brew install ffmpeg`)
- **Chrome ou Chromium** (necessário para gerar Reels via `gerar-video-mp4`)
- **Bun** (`brew install bun`) — runtime que executa o puppeteer-core do render de Reels
- Claude Code instalado
- **Pelo menos um provider de imagem** (escolha um — você precisa de só um):
  - **Recomendado:** ChatGPT Plus/Team + Codex CLI (`npm install -g @openai/codex` e `codex login`) — desbloqueia gpt-image-2 com melhor tipografia
  - **Alternativa grátis:** chave Gemini (https://aistudio.google.com/apikey) salva em `~/.operacao-ia/config/gemini.env`
  - **Fallback opcional:** conta Higgsfield AI (MCP) — não obrigatória
- **Transcrição (opcional, melhora muito o repurpose):** chave ElevenLabs (free tier ~10h/mês em https://elevenlabs.io/app/sign-up). Whisper local cobre como fallback.

## Plataformas cobertas

YouTube longo + Shorts · Instagram Reels + Carrossel + Stories · TikTok · LinkedIn (post + carrossel PDF)

Sem integração de API de publicação — o material é gerado e você publica manualmente.

## Após instalar

Comandos prontos:

| Comando | O que faz |
|---|---|
| `criar reel sobre [tópico]` | Reel/Short animado em MP4 (HTML + ffmpeg) |
| `gerar carrossel [N] slides sobre [tema] para linkedin` | Carrossel com copy + imagens AI |
| `thumb yt: [título]` | 3 variantes de thumbnail 1280×720 |
| `gerar copy post [plataforma] sobre [tema]` | Legenda + hashtags + CTA pra Instagram/LinkedIn/TikTok/YouTube |
| `repurpose [caminho do vídeo]` | Live longa → pacote multi-plataforma (ElevenLabs ou Whisper) |
| `agente social` | Menu com todas as opções |

## Suporte

Comunidade ZX Control · Aula MasterClass: [zx-control.zxlab.com.br](https://zx-control.zxlab.com.br)
