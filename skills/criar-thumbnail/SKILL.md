---
name: criar-thumbnail
description: "Gera 3 variantes de thumbnail YouTube (1280x720) via Higgsfield AI. Variantes: A (rosto+texto), B (conceitual), C (comparação/antes-depois). Lê DESIGN.md para manter identidade visual. Use SEMPRE que o aluno disser: criar thumbnail, gerar thumb, thumb yt, thumbnail youtube, capa do video, capa youtube, thumbnail, miniatura youtube."
model: sonnet
effort: low
---

# Criar Thumbnail YouTube

Gera 3 thumbnails YouTube (1280×720) em estilos diferentes pra o aluno escolher ou testar A/B.

## Carregamento de contexto

- `~/.operacao-ia/config/marca.json`
- `~/.operacao-ia/data/social-media/DESIGN.md`

## Inputs obrigatórios

1. **Título do vídeo** — ex: "Eu testei IA por 30 dias — esse foi o resultado"
2. **Tipo de vídeo** — `tutorial`, `vlog`, `analise`, `entrevista`, `comparacao`. Default: `tutorial`
3. **Texto curto pra thumb** — 3-5 palavras máximo (default: extrair do título). Ex: "30 DIAS DE IA"
4. **Output dir** — `~/.operacao-ia/data/social-media/output/thumbs/YYYY-MM-DD_<slug>/`

## Fluxo

### 1. Definir as 3 variantes

| Variante | Conceito | Prompt-base |
|---|---|---|
| A | Rosto expressivo + texto grande | "close-up portrait, surprised/intrigued expression, bold text overlay '<texto>'" |
| B | Conceitual/metáfora visual | "metaphorical visual representing '<tema>', no faces, strong visual hook" |
| C | Comparação/contraste | "split composition: before vs after / problem vs solution, visual contrast" |

Use a seção "Para Higgsfield" do DESIGN.md como base estética.

### 2. Geração via Higgsfield

Para cada variante chame `mcp__higgsfield__generate_image` com:

```
prompt: "{base_do_DESIGN.md}, YouTube thumbnail 1280x720,
         {conceito_da_variante}, text '<texto>' rendered bold and readable,
         high contrast, attention-grabbing, no embedded watermarks"
aspect_ratio: "16:9"
quality: high
```

Importante: pedir `aspect_ratio=16:9` resulta em 1280×720. Se Higgsfield retornar outro tamanho, fazer resize com Pillow:

```python
from PIL import Image
img = Image.open('raw.png')
img.thumbnail((1280, 720), Image.LANCZOS)
canvas = Image.new('RGB', (1280, 720), (0, 0, 0))
x = (1280 - img.width) // 2
y = (720 - img.height) // 2
canvas.paste(img, (x, y))
canvas.save('thumb-A.png', 'PNG', optimize=True)
```

### 3. Output

Salve:
```
output/thumbs/<YYYY-MM-DD>_<slug>/thumb-A-rosto.png
output/thumbs/<YYYY-MM-DD>_<slug>/thumb-B-conceitual.png
output/thumbs/<YYYY-MM-DD>_<slug>/thumb-C-comparacao.png
output/thumbs/<YYYY-MM-DD>_<slug>/README.txt   # explicação das 3 variantes + recomendação A/B teste
```

### 4. Atualizar galeria

Leia `~/.operacao-ia/data/social-media/gallery.json`, append em `data["items"]`, escreva de volta. Item:

```json
{ "type": "thumbnail", "title": "<título do vídeo>", "path": "output/thumbs/<dir>/", "created_at": "<ISO>" }
```

### 5. Resumo

- Mostre os 3 paths
- Explique brevemente cada estilo
- Sugira: "Comece com a A (rosto). Se o CTR for <3% em 24h, troque pela B."
- Lembre: tamanho final deve ser ≤2MB pra subir no YouTube (se passar, comprimir com `pngquant` ou re-save Pillow com `optimize=True`)

## Não fazer

- Não use Puppeteer ou HTML pra compor — Higgsfield direto.
- Não gere thumbnail com rosto do criador real (deep-fake) sem permissão explícita dele.
- Não use textos longos na thumb (>5-6 palavras).
