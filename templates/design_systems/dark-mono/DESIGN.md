# DESIGN.md — Dark Mono

Sistema visual minimalista escuro com mono-fonte. Ideal para tech, finance, B2B, IA.

## Cores

| Token | Valor | Uso |
|---|---|---|
| `bg-primary`   | `#0a0a0b` | Fundo principal |
| `bg-card`      | `#141416` | Cards, painéis |
| `bg-elevated`  | `#1c1c1f` | Hover, modais |
| `fg-primary`   | `#ededed` | Texto principal |
| `fg-muted`     | `#8a8a8d` | Texto secundário |
| `fg-subtle`    | `#5a5a5d` | Captions |
| `accent`       | `#e5e5e7` | Destaque (branco-quente) |
| `accent-alt`   | `#ffd60a` | Highlight (âmbar) |
| `border`       | `#27272a` | Bordas finas |
| `success`      | `#22c55e` | Indicadores positivos |
| `danger`       | `#ef4444` | Erros |

Higgsfield prompts: "dark minimalist background, near-black `#0a0a0b`, subtle warm-white accents `#ededed`, occasional amber highlight `#ffd60a`, high contrast, no gradients".

## Tipografia

- **Display + Body:** `JetBrains Mono` (fallback: `ui-monospace`, `SF Mono`, `Consolas`)
- **Pesos:** 400 (regular), 500 (medium), 600 (semibold) — sem bold pesado
- **Tamanhos base (px):** display 32, h1 24, h2 18, body 15, small 13, micro 11
- **Espaçamento de linha:** 1.5 para body, 1.25 para títulos
- **Letter-spacing:** -0.5px em títulos, 0.3px em uppercase

## Espaçamento

Escala 4px: `4, 8, 12, 16, 24, 32, 48, 64`. Sem half-steps.

## Estilo visual

- **Bordas:** 1px sólidas em `border`. Nunca shadows pesados.
- **Cantos:** 4px (cards), 6px (botões), 0 (tabelas, inputs).
- **Hover:** muda `bg-card` → `bg-elevated`. Sem animações além de `opacity` e `background-color`.
- **Ícones:** outline 1.5px stroke, nunca filled.
- **Imagens:** preto-e-branco ou duotone (escuro + accent). Nunca colorido cheio.

## Componentes

- **Botão primário:** fundo `accent`, texto `bg-primary`, padding `8px 16px`, radius 6px.
- **Botão secundário:** fundo transparente, border `border`, texto `fg-primary`.
- **Card:** `bg-card` + border `border` + radius 4px + padding 24px.
- **Tag:** uppercase, tracking 0.5px, fundo transparente, border `border`, texto `fg-muted`.

## Para Higgsfield (prompts visuais)

Adicionar sempre ao prompt: "dark monochrome aesthetic, near-black `#0a0a0b` background, warm-white text `#ededed`, subtle amber accent `#ffd60a`, mono spaced typography vibe, high contrast, minimalist, no gradients, no decorative elements, editorial composition, generous negative space".
