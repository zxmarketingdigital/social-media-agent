# DESIGN.md — Light Editorial

Sistema visual claro editorial com serif. Ideal para lifestyle, wellness, educação, coaching.

## Cores

| Token | Valor | Uso |
|---|---|---|
| `bg-primary`   | `#fafaf7` | Fundo principal (off-white quente) |
| `bg-card`      | `#ffffff` | Cards, painéis |
| `bg-elevated`  | `#f3f3ef` | Hover |
| `fg-primary`   | `#1a1a1a` | Texto principal |
| `fg-muted`     | `#5c5c5c` | Texto secundário |
| `fg-subtle`    | `#8e8e8e` | Captions |
| `accent`       | `#9b5e3c` | Terracota (destaque editorial) |
| `accent-alt`   | `#3d5a4e` | Verde-musgo (secundário) |
| `border`       | `#e6e3dd` | Bordas suaves |
| `success`      | `#558b6e` | Indicadores positivos |
| `danger`       | `#a64340` | Erros |

Higgsfield prompts: "light editorial aesthetic, warm off-white background `#fafaf7`, dark text `#1a1a1a`, terracotta accent `#9b5e3c`, museum-catalog vibe, soft natural light".

## Tipografia

- **Display:** `Playfair Display` (serif elegante, fallback `Georgia`, `Times`)
- **Body:** `Inter` (fallback `system-ui`)
- **Pesos:** display 400-700, body 400-600
- **Tamanhos base (px):** display 36, h1 28, h2 20, body 16, small 14, micro 12
- **Espaçamento de linha:** 1.6 para body, 1.2 para títulos serif
- **Letter-spacing:** 0 em títulos, 0.2px em body

## Espaçamento

Escala 4px: `4, 8, 12, 16, 24, 32, 48, 64, 96`. Generoso em padding vertical.

## Estilo visual

- **Bordas:** 1px sólidas em `border` (apenas onde necessário).
- **Cantos:** 8px (cards), 24px (botões pílula), 0 (imagens artísticas).
- **Hover:** translateY(-2px) + leve sombra `0 4px 12px rgba(0,0,0,0.08)`.
- **Ícones:** estilo line-art, 1.5px stroke, podem ter pequenos detalhes filled.
- **Imagens:** coloridas em paleta natural, com grão de filme leve. Composição assimétrica, regra dos terços.

## Componentes

- **Botão primário:** fundo `accent`, texto `bg-card`, padding `12px 24px`, radius 24px (pílula).
- **Botão secundário:** fundo `bg-card`, border 1px `accent`, texto `accent`.
- **Card:** `bg-card` + sombra suave + radius 8px + padding 32px.
- **Tag:** serif italic, texto `fg-muted`, sem border.

## Para Higgsfield (prompts visuais)

Adicionar sempre: "light editorial photography aesthetic, warm off-white `#fafaf7` background, deep terracotta accent `#9b5e3c`, soft natural lighting, fine art magazine composition, serif typography vibe, generous negative space, subtle film grain, asymmetric layout, no harsh shadows".
