# Social Media Agent — ZX Control Semana 7

Pacote de criação de conteúdo para redes sociais que roda direto no Claude Code do aluno.

## O que está incluído

**6 skills especialistas:**
- `criar-reel` — Reels/Shorts/TikToks com avatar AI ou animação (Higgsfield)
- `gerar-carrossel` — Carrosséis Instagram/LinkedIn com imagens AI (Higgsfield) + copy (Claude)
- `criar-thumbnail` — 3 variantes de thumb YouTube (Higgsfield)
- `repurpose-conteudo` — Live de 1h → cortes + Reels + carrossel + copys (Whisper + video-use + Higgsfield)
- `gerar-copy-post` — Legenda + hashtags + CTA por plataforma (Claude)
- `agente-social-media` — Orquestrador com menu numérico

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
- ffmpeg
- Conta no Higgsfield AI (grátis ou paga) — MCP é conectado durante o setup
- Claude Code instalado

## Plataformas cobertas

YouTube longo + Shorts · Instagram Reels + Carrossel + Stories · TikTok · LinkedIn (post + carrossel PDF)

Sem integração de API de publicação — o material é gerado e você publica manualmente.

## Após instalar

Comandos prontos:

| Comando | O que faz |
|---|---|
| `criar reel sobre [tópico]` | Reel/Short com avatar AI ou animado |
| `gerar carrossel [N] slides sobre [tema] para linkedin` | Carrossel com copy + imagens AI |
| `thumb yt: [título]` | 3 variantes de thumbnail 1280×720 |
| `stories da semana` | 7 stories 9:16 (segunda a domingo) |
| `repurpose [caminho do vídeo]` | Live longa → pacote multi-plataforma |
| `agente social` | Menu com todas as opções |

## Suporte

Comunidade ZX Control · Aula MasterClass: [zx-control.zxlab.com.br](https://zx-control.zxlab.com.br)
