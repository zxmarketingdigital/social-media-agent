---
name: criar-reel
description: "Gera Reel/Short/TikTok 9:16 (ou Reel feed 4:5) com hook + corpo + CTA. Roteiro escrito pelo Claude, vídeo animado gerado via skill `gerar-video-mp4` (Chrome headless + ffmpeg) no estilo dos anúncios ZX LAB. Lê marca.json e DESIGN.md para manter identidade. Use SEMPRE que o aluno disser: criar reel, novo reel, gerar reel, reel sobre, criar shorts, novo shorts, criar tiktok, video curto, reel instagram, criativo reels."
model: sonnet
effort: medium
---

# Criar Reel/Short/TikTok

Skill para gerar 1 vídeo vertical curto pronto pra publicar no Instagram Reels, TikTok ou YouTube Shorts. Usa a mesma engine que produz os anúncios do ZX LAB (HTML animado → MP4 via Chrome headless + ffmpeg) — não depende de plano pago da Higgsfield.

## Por que mudou (importante)

Versões antigas dessa skill chamavam o Higgsfield para gerar vídeo. **O plano grátis da Higgsfield não gera vídeo** — só imagem. Para evitar travar o aluno num upgrade, a geração agora é local via `gerar-video-mp4` (skill instalada no mesmo Setup 7). Se o aluno tiver Higgsfield pago e quiser usar avatar AI real, a seção "Modo Higgsfield (opcional)" no final mostra como alternar.

## Carregamento de contexto

Sempre leia antes de gerar:

- `~/.operacao-ia/config/marca.json` — nome, nicho, persona, tom, público
- `~/.operacao-ia/data/social-media/DESIGN.md` — design system (paleta, tipografia, estilo)

Se algum arquivo faltar, peça o aluno rodar `python3 setup/setup_marca.py` ou `setup_design_system.py`.

## Inputs obrigatórios

Coletar do aluno (uma pergunta por vez se faltarem):

1. **Tema do Reel** — frase curta, ex: "como usar IA no atendimento de pequenos negócios"
2. **Plataforma** — `instagram`, `tiktok`, `shorts`. Default: `instagram` (afeta CTA e hashtags)
3. **Duração** — `15s`, `30s`, `60s`. Default: `30s`
4. **Aspect ratio** — `9:16` (default, 1080×1920) ou `4:5` (feed, 1080×1350)

## Fluxo

### 1. Roteiro

Escreva o roteiro do Reel SEM gerar nada ainda. Estrutura:

- **Hook (0-3s)** — frase de impacto que prende atenção. Lembre da regra: deve criar curiosidade ou gerar identificação imediata.
- **Corpo (3s até duração-3s)** — 2 a 4 ideias-chave entregando valor. Use bullets curtos, máximo 1 linha cada.
- **CTA (últimos 3s)** — call-to-action específico da plataforma:
  - Instagram: "Salva pra usar depois e me segue pra mais"
  - TikTok: "Segue pra parte 2"
  - Shorts: "Inscreve no canal pra ver o vídeo completo"

Tom = `marca.tom`. Linguagem adaptada ao `marca.publico`.

Mostre o roteiro ao aluno e peça confirmação antes de gerar o vídeo.

### 2. Montar HTML animado (estilo anúncio ZX LAB)

Crie um diretório de trabalho em `~/.operacao-ia/data/social-media/output/reels/_render/<slug>/` com `frames/`, `out/`, `assets/`.

Crie `scene.html` seguindo as regras OBRIGATÓRIAS da skill `gerar-video-mp4`:

- Dimensões fixas no `html, body`: `1080x1920` (9:16) ou `1080x1350` (4:5).
- Fontes Inter + JetBrains Mono via Google Fonts (ou as fontes do DESIGN.md se diferentes).
- Paleta lida do DESIGN.md (`marca.cores.primary`, `accent`, `bg`, etc).
- Função `window.SET_TIME(t)` controla **TUDO** via JS (opacity/transform). Sem CSS keyframes/transitions — não funcionam em render headless.

Estrutura visual sugerida (3-4 cenas):

| Cena | Tempo | O que aparece |
|---|---|---|
| 1 — Hook | 0–3s | Texto grande (Inter 800/900) com a frase do hook, fade-in + slide-up. Logo da marca canto superior. |
| 2 — Pontos | 3s até duração-3s | Bullets aparecendo um por um (stagger 400-600ms), com underline animado em cor accent. |
| 3 — CTA | últimos 3s | CTA grande + handle/@ da marca + microcopy ("salva e segue"). |
| 4 — End card | últimos 0.5s | Frame estático com logo e cor primária pra fechar. |

**Anti-AI-slop:** se houver mockup/print real relacionado ao tema em `~/.operacao-ia/data/social-media/assets/`, usar como background ou frame em vez de inventar UI com CSS. Copiar pra `assets/` do projeto antes de referenciar.

### 3. Renderizar via `gerar-video-mp4`

A skill `gerar-video-mp4` é um **runbook** — não um helper CLI parametrizado. Você (Claude) lê o SKILL.md dela e gera `render.mjs` + comando ffmpeg AD-HOC dentro do diretório do projeto, com os valores corretos hardcoded para esta cena. Constantes que precisam ser injetadas no `render.mjs`:

| Constante | Valor pra Reel 9:16 | Valor pra Reel 4:5 |
|---|---|---|
| `W` (width) | `1080` | `1080` |
| `H` (height) | `1920` | `1350` |
| `FPS` | `25` (padrão) ou `60` (se aluno pedir suave) | idem |
| `DURATION` | `15`, `30` ou `60` conforme escolha do aluno | idem |
| `CHROME_PATH` | resultado de `Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').exists()` ou `shutil.which('google-chrome')`/`'chromium'` | idem |
| `FFMPEG` | `command -v ffmpeg` (NUNCA hardcodar `/opt/homebrew/Cellar/...`) | idem |

Antes de renderizar, **smoke test obrigatório**:
1. Abrir `scene.html` no Chrome local: `open scene.html` — confirmar visualmente que animação roda e `window.SET_TIME(t)` controla os elementos.
2. Validar que `bun` está instalado (`shutil.which('bun')`); se não, instruir o aluno: `brew install bun` antes de prosseguir.
3. Validar espaço em disco: 1500 frames PNG 1080×1920 ≈ 300-600MB; abortar se `df -h .` mostrar <2GB livres.

A skill `gerar-video-mp4` produz `out/video.mp4` (não `out/reel.mp4` — atenção ao nome). Depois do render, limpar `frames/` para não acumular GBs de PNG entre Reels.

Tempo típico: ~5-15s de render para 30s de vídeo num M1.

### 4. Salvar no destino final

Mover `out/video.mp4` para o destino final renomeado:
```
~/.operacao-ia/data/social-media/output/reels/YYYY-MM-DD_<slug-do-tema>.mp4
~/.operacao-ia/data/social-media/output/reels/YYYY-MM-DD_<slug-do-tema>.copy.txt
```

Onde `<slug-do-tema>` é o tema em kebab-case (`como-usar-ia-no-atendimento`).

`.copy.txt` contém:
- Roteiro completo (hook + corpo + CTA)
- Legenda sugerida pra postagem (chame `gerar-copy-post` internamente se quiser)
- Hashtags sugeridas (8-12, mix de nicho + amplas)

### 5. Atualizar galeria

Leia `~/.operacao-ia/data/social-media/gallery.json` (criado pelo `setup_dashboard.py` com `{"items": []}`), faça append em `data["items"]` e escreva de volta. Item:

```json
{ "type": "reel", "title": "<tema>", "path": "output/reels/...", "platform": "instagram", "engine": "gerar-video-mp4", "created_at": "<ISO>" }
```

### 6. Resumo final

Mostre ao aluno:
- Path do MP4 gerado
- Path do copy
- Sugestão de horário pra publicar baseado no nicho (manhã pra B2B, fim de tarde pra B2C)
- Comando pra abrir no Finder: `open ~/.operacao-ia/data/social-media/output/reels/`

## Modo Higgsfield (opcional — só se aluno tiver plano pago)

Se o aluno explicitamente disser "usar Higgsfield" ou "avatar AI real", e o MCP `higgsfield` estiver conectado:

- Pergunte o plano dele primeiro: "Plano grátis não gera vídeo, só imagem. Você tem plano pago da Higgsfield?"
- Se sim, chame `mcp__higgsfield__generate_video` com `script`, `aspect_ratio`, `duration_seconds`, `style_prompt` extraído do DESIGN.md.
- Se não, redirecione pro fluxo padrão (HTML → gerar-video-mp4) sem cobrar upgrade.

## Tratamento de erro

- **Chrome não encontrado:** instrua a baixar de google.com/chrome — `gerar-video-mp4` não roda sem ele.
- **ffmpeg não encontrado:** `brew install ffmpeg`.
- **Render lento (>2min):** confirme que `gerar-video-mp4` está usando o pipeline puppeteer (não Playwright completo) e que `fps=25` (padrão). Suba pra 60 só se aluno pedir.
- **HTML quebrado:** valide com `open scene.html` no browser antes de renderizar — se animação não roda no browser, também não vai renderizar.

## Não fazer

- **Não dependa de plano pago da Higgsfield** — o fluxo padrão deve ser 100% local.
- Não suba pra YouTube/IG/TikTok automaticamente — esse Setup é manual.
- Não use CSS keyframes pra animação — só `window.SET_TIME(t)` em JS (regra do `gerar-video-mp4`).
- Não invente API keys — `gerar-video-mp4` roda local sem chave nenhuma.
