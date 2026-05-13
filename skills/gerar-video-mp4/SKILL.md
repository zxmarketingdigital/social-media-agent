---
name: gerar-video-mp4
description: "Gera vídeo MP4 a partir de animação HTML via pipeline puppeteer + Chrome headless + ffmpeg. Use SEMPRE que o usuário disser: gerar video, criar mp4, exportar mp4, render mp4, animação para reels, hero animation, criativo animado, video para anuncio, video para feed, video stories, animação produto, video promocional, animar landing page, animar lp, criar criativo video, gerar criativo, mp4 instagram, video tiktok, video youtube short, animação curso, video curso, vídeo demo. Diferente de criar-demo-skill (animação terminal ASCII) — esta skill gera vídeo visual gráfico (mockups reais, tipografia, motion design)."
model: sonnet
effort: medium
---

# /gerar-video-mp4 — Render de Vídeo MP4 a partir de HTML Animado

## Quando usar

Sempre que o usuário pedir vídeo MP4 visual gráfico (NÃO terminal/ASCII):
- Reels/Feed Instagram (1080×1350)
- Stories/TikTok (1080×1920)
- YouTube hero/thumbnail animado (1920×1080)
- Hero animation pra LP
- Criativo de anúncio
- Demo de produto

## NÃO usar quando

- Animação terminal ASCII com spinners/progress bars → usar `/criar-demo-skill`
- Vídeo de pessoa falando ou screen recording → usar `/video-use`
- Cortes de masterclass Zoom → usar `/youtube-cortes-masterclass`

## Pipeline obrigatório

### 1. Setup pasta projeto

```bash
PROJ=~/projetos/<slug>/<subpasta>  # ou ~/projetos/<slug>-video/
mkdir -p $PROJ/{frames,out,assets}
```

Se houver mockups/imagens reais relacionadas, COPIAR pra `$PROJ/assets/`. **Anti-AI-slop:** nunca recriar produtos/UIs com CSS/SVG quando há JPG/PNG real disponível.

### 2. Criar `scene.html`

Estrutura obrigatória do HTML:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>...</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  /* DIMENSÃO FIXA — usar dimensão alvo */
  html, body { width:1080px; height:1350px; overflow:hidden; }
  /* Design system ZX LAB ou do projeto */
</style>
</head>
<body>
<div id="stage">
  <!-- cenas com .scene -->
</div>
<script>
const DURATION = 10.0;  // segundos
const scenes = [...];

window.SET_TIME = function(t) {
  // Controla TODAS animações baseado em t (0..DURATION)
  // CSS keyframes/transitions NÃO funcionam pra render headless
  // Tudo via JS setting opacity/transform/etc
};

if (!window.HEADLESS) {
  let start = performance.now();
  function loop(now) {
    let t = ((now - start) / 1000) % DURATION;
    window.SET_TIME(t);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}
window.SET_TIME(0);
</script>
</body>
</html>
```

**Regras críticas HTML:**
- `window.SET_TIME(t)` controla todo movimento — não usar `@keyframes` ou `transition` (não capturáveis frame-a-frame)
- Easing functions inline: `easeOutCubic = x => 1 - Math.pow(1-x, 3)`
- Stagger reveals via `.forEach((el, i) => { delay = i*0.16 })`
- Set `window.HEADLESS = true` via puppeteer pra desligar requestAnimationFrame loop
- Fontes Google: aguardar 2s no render pra não capturar fallback fonts

### 3. Criar `render.mjs`

```js
import puppeteer from 'puppeteer-core';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const HTML = 'file://' + path.join(__dirname, 'scene.html');
const FRAMES_DIR = path.join(__dirname, 'frames');
const FPS = 30;
const DURATION = 10.0;
const W = 1080, H = 1350;

if (!fs.existsSync(FRAMES_DIR)) fs.mkdirSync(FRAMES_DIR, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--hide-scrollbars', '--font-render-hinting=none', '--disable-gpu-vsync', '--force-device-scale-factor=1'],
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await page.evaluateOnNewDocument(() => { window.HEADLESS = true; });
await page.goto(HTML, { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 2000));  // aguardar fontes Google

const total = Math.floor(DURATION * FPS);
console.log(`Rendering ${total} frames at ${W}x${H}...`);
const t0 = Date.now();
for (let i = 0; i < total; i++) {
  const t = i / FPS;
  await page.evaluate((t) => window.SET_TIME(t), t);
  await page.screenshot({
    path: path.join(FRAMES_DIR, `f${String(i).padStart(4, '0')}.png`),
    type: 'png'
  });
  if (i % 30 === 0) {
    process.stdout.write(`\r[${i}/${total}] ${((Date.now()-t0)/1000).toFixed(1)}s`);
  }
}
console.log(`\nDone in ${((Date.now()-t0)/1000).toFixed(1)}s`);
await browser.close();
```

### 4. Instalar puppeteer-core (uma vez)

```bash
# Reusar de projeto existente se possível:
ln -sf ~/projetos/agencia-ia-50k-demo-huashu/node_modules ./node_modules

# Ou instalar fresh:
cd $PROJ && bun add puppeteer-core
```

### 5. Render frames

```bash
cd $PROJ && bun render.mjs
```

Timings esperados (Apple M-series):
- 1080×1350 · 10s @ 30fps (300 frames): ~42s
- 1080×1350 · 12s @ 30fps (360 frames): ~52s
- 1920×1080 · 10s @ 30fps: ~50s

### 6. Encode MP4 H.264

```bash
FFMPEG=/opt/homebrew/Cellar/ffmpeg/8.1_1/bin/ffmpeg
$FFMPEG -y -framerate 30 -i frames/f%04d.png \
  -c:v libx264 -pix_fmt yuv420p \
  -crf 17 -preset slow \
  -movflags +faststart \
  out/video.mp4
```

**CRF reference:**
- 17 = alta qualidade (~1.8MB / 10s 1080×1350)
- 18 = padrão recomendado (~1.3MB)
- 23 = média qualidade (~0.8MB)

### 7. Validar e abrir

```bash
ls -lh out/video.mp4
open out/video.mp4  # abre QuickTime
```

## Padrões de cena (template 5 atos · 10s)

Para vídeos promocionais ZX LAB, estrutura recomendada:

| Cena | Duração | Conteúdo |
|---|---|---|
| 1. Hook | 2-2.5s | Pergunta provocativa OU stat impactante OU "antes" |
| 2. Problema | 2-2.5s | Jeito antigo riscado (mostrar dor concreta) |
| 3. Solução | 2-3s | Terminal Claude Code com comando real + outputs ✓ |
| 4. Prova | 1.5-2s | Mockups reais (NÃO CSS/SVG) com pulse live |
| 5. CTA | 1.5-2s | Headline impacto + botão âmbar + URL |

## Anti-AI-slop checklist

Antes de finalizar, verificar:
- [ ] Mockups reais usados (JPG/PNG copiados pra assets/), não shapes CSS
- [ ] Terminal commands reais (não "cmd1 cmd2 cmd3" placeholder)
- [ ] Tipografia: Inter + JetBrains Mono (design system ZX LAB) OU do projeto
- [ ] Cores do design system: âmbar #D97706 + bg #0A0A0A → #111111 (ou DESIGN.md local)
- [ ] Sem partículas genéricas, orbs, gradientes flat
- [ ] Sem emoji decorativo (exceto se brand do produto usa)
- [ ] Stagger reveals sutis (fade + translateY 30-40px), não bouncy/cartoon
- [ ] Easing: easeOutQuart/Cubic (não linear)

## Watermark Huashu (opcional)

Se animação foi criada usando referências da skill huashu-design, adicionar:

```html
<div style="position:absolute; bottom:24px; right:32px; z-index:11;
            font-family:'JetBrains Mono',monospace; font-size:10px;
            color:rgba(255,255,255,0.28); letter-spacing:0.18em;
            pointer-events:none;">
  CREATED BY HUASHU-DESIGN
</div>
```

## Variantes de output

Após gerar 1 versão, oferecer:
- **GIF palette-optimized** (`ffmpeg -vf palettegen → palette → palette use`)
- **60fps interpolado** (motion smoothing)
- **Versão muted vs com áudio** (`~/.claude/skills/huashu-design/scripts/add-music.sh`)
- **Resoluções alternativas** (Stories 9:16, YouTube 16:9)

## Adicionar ao launcher (opcional)

Se vídeo for hero pra LP local:

```bash
ln -sfn $PROJ ~/.zxlab-sites/<alias>
# Editar ~/.zxlab-sites/launcher.html section "Design & Demos" — adicionar card
# Validar: curl -s -o /dev/null -w "%{http_code}" http://localhost:8891/<alias>/scene.html
```

Detalhes em `feedback_launcher_symlink_pattern.md` na memória.

## Tools/paths fixos

- `ffmpeg`: `/opt/homebrew/Cellar/ffmpeg/8.1_1/bin/ffmpeg`
- `Chrome`: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- `puppeteer-core`: instalado em `~/projetos/agencia-ia-50k-demo-huashu/node_modules` (reusar via symlink)
- Design system padrão: `~/projetos/zx-control-lp/DESIGN.md` (ou local DESIGN.md do projeto)

## Referência de exemplos

Vídeos já gerados com este pipeline:
- `~/projetos/agencia-ia-50k-demo-huashu/out/agencia-ia-50k-demo.mp4` — 12s 1080×1350
- `~/projetos/agencia-ia-automatizada-claude-code/docs/hero-animation-huashu/out/hero-animation.mp4` — 10s 1080×1350
