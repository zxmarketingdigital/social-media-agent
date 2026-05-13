# DESIGN.md — Vivid Pop

Sistema visual colorido vibrante. Ideal para entretenimento, food, fitness, lifestyle jovem.

## Cores

| Token | Valor | Uso |
|---|---|---|
| `bg-primary`   | `#0f0f12` | Fundo escuro intenso |
| `bg-card`      | `#1a1a20` | Cards |
| `bg-elevated`  | `#23232b` | Hover |
| `fg-primary`   | `#ffffff` | Texto principal |
| `fg-muted`     | `#a0a0b0` | Texto secundário |
| `accent`       | `#ff3d8a` | Magenta vibrante (destaque) |
| `accent-2`     | `#06d6a0` | Verde-neon (secundário) |
| `accent-3`     | `#ffd23f` | Amarelo elétrico |
| `gradient-1`   | `linear-gradient(135deg, #ff3d8a, #7b2cbf)` | Botões/banners |
| `gradient-2`   | `linear-gradient(135deg, #06d6a0, #118ab2)` | Highlights |
| `border`       | `#2a2a35` | Bordas |
| `danger`       | `#ff5470` | Erros |

Higgsfield prompts: "vivid pop aesthetic, magenta `#ff3d8a` and neon green `#06d6a0` accents, dark background `#0f0f12`, electric energetic, high saturation, bold gradients".

## Tipografia

- **Display:** `Space Grotesk` (geometric sans, fallback `Inter`)
- **Body:** `Inter`
- **Pesos:** display 600-800, body 400-600
- **Tamanhos base (px):** display 40, h1 28, h2 20, body 16, small 14, micro 12
- **Espaçamento de linha:** 1.5 para body, 1.1 para títulos
- **Letter-spacing:** -1px em títulos display, 0 em body

## Espaçamento

Escala 4px: `4, 8, 12, 16, 24, 32, 48`. Compacto, com elementos próximos para energia.

## Estilo visual

- **Bordas:** 1-2px com `accent` em destaques. Glow sutil em hover (`0 0 16px rgba(255,61,138,0.4)`).
- **Cantos:** 12px (cards), 999px (botões pílula totalmente arredondados), 8px (imagens).
- **Hover:** scale(1.02) + glow + leve rotação 1° em ícones.
- **Ícones:** filled colorido, podem ter pequenas animações.
- **Imagens:** alta saturação, contraste forte, podem ter overlays gradientes.

## Componentes

- **Botão primário:** `gradient-1`, texto `fg-primary`, padding `14px 28px`, radius 999px.
- **Botão secundário:** fundo `bg-card`, border 2px `accent`, texto `accent`.
- **Card:** `bg-card` + border 1px `border` + radius 12px + padding 20px + hover glow.
- **Tag:** fundo `accent` + 20% opacity, texto `accent`, radius 999px, padding `4px 12px`, uppercase tracking 0.5px.

## Para Higgsfield (prompts visuais)

Adicionar sempre: "vivid pop aesthetic, dark background `#0f0f12`, vibrant magenta `#ff3d8a` and neon green `#06d6a0` accents, electric energy, high saturation, bold geometric typography, gradients magenta-to-purple, dynamic compositions, motion blur hints, urban energetic vibe, Y2K-inspired".
