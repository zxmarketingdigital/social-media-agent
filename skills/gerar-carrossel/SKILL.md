---
name: gerar-carrossel
description: "Gera carrossel para Instagram (PNGs 1080x1350 ou 1080x1080) ou LinkedIn (PDF). Claude escreve a copy de cada slide; Higgsfield AI gera as imagens lendo DESIGN.md. Use SEMPRE que o aluno disser: criar carrossel, gerar carrossel, novo carrossel, carrossel ig, carrossel instagram, carrossel linkedin, post educativo, post em slides, slides instagram, carousel."
model: sonnet
effort: medium
---

# Gerar Carrossel

Cria carrossel multi-slide com texto + imagem AI, pronto pra publicar no Instagram ou LinkedIn.

## Carregamento de contexto

Sempre leia antes:
- `~/.operacao-ia/config/marca.json`
- `~/.operacao-ia/data/social-media/DESIGN.md`

## Inputs obrigatórios

1. **Tema/título do carrossel** — ex: "5 erros que matam o LinkedIn de empreendedor B2B"
2. **Plataforma** — `instagram` (PNGs separados) ou `linkedin` (PDF + PNGs). Default: `instagram`
3. **Número de slides** — entre 5 e 10. Default: 7
4. **Aspect ratio** — `4:5` (1080×1350, IG feed vertical, recomendado), `1:1` (1080×1080), ou A4 paisagem (LinkedIn)
5. **Output dir** — default: `~/.operacao-ia/data/social-media/output/carrosseis/YYYY-MM-DD_<slug>/`

## Fluxo

### 1. Estrutura do carrossel

Escreva a copy de cada slide ANTES de gerar imagens. Estrutura padrão:

- **Slide 1 (Capa)** — Hook + nome do criador (de `marca.nome`)
- **Slide 2 (Problema)** — Dor/contexto que o leitor reconhece
- **Slides 3 a N-1 (Conteúdo)** — Pontos numerados ou framework
- **Slide N (CTA)** — Call-to-action: "Salvou? Salva no perfil pra reler. Me segue pra mais."

Tom = `marca.tom`. Para LinkedIn, tom mais formal. Para Instagram, mais direto.

Limite de texto por slide: máximo 50 palavras (carrossel não é blog).

Mostre os textos ao aluno e peça aprovação antes de gerar imagens.

### 2. Geração das imagens via Higgsfield

Para cada slide, chame `mcp__higgsfield__generate_image` (ou equivalente).

**Estratégia de prompt:**
- Use a seção "Para Higgsfield" do DESIGN.md como base
- Adicione contexto do slide (capa = mais impactante, conteúdo = limpo com espaço pra texto, CTA = energia)
- Inclua o texto do slide no prompt para o Higgsfield posicionar tipografia + composição ao redor

**Exemplo de prompt:**
```
{prompt_base_do_DESIGN.md}, slide 3 of 7 in a carousel, theme: "{tema}",
text overlay: "{texto_curto_do_slide}", composition: clean center-aligned text
with visual element below, dimensions {aspect_ratio}
```

**Parâmetros:**
- `prompt`: como acima
- `aspect_ratio`: conforme escolha
- `quality`: alta (default Higgsfield)

### 3. Composição (Instagram)

Salve cada PNG como:
```
output/carrosseis/<YYYY-MM-DD>_<slug>/slide-01-capa.png
output/carrosseis/<YYYY-MM-DD>_<slug>/slide-02-problema.png
...
output/carrosseis/<YYYY-MM-DD>_<slug>/slide-07-cta.png
output/carrosseis/<YYYY-MM-DD>_<slug>/copy.txt   # legenda + hashtags
```

### 4. Composição (LinkedIn)

Para LinkedIn, gere os PNGs em formato A4 paisagem ou 1:1, depois junte em PDF usando `python3 -c "from PIL import Image; ..."`:

```python
from PIL import Image
from pathlib import Path
slides = sorted(Path('output/carrosseis/<dir>/').glob('slide-*.png'))
imgs = [Image.open(p).convert('RGB') for p in slides]
imgs[0].save('output/carrosseis/<dir>/carrossel.pdf', save_all=True, append_images=imgs[1:])
```

(Pillow é dependência padrão do video-use — disponível em `~/.operacao-ia/tools/video-use/.venv/bin/python`.)

### 5. Legenda pra postagem

Escreva no `copy.txt`:
- Primeira linha = hook do slide 1 (chama atenção no feed)
- Corpo = expansão do framework (3-5 linhas)
- CTA do slide N
- Hashtags: 8-12 misturando nicho + amplas, separadas por espaço, ao final
- Separar tudo com `\n\n` (linha em branco)

### 6. Atualizar galeria

Append em `gallery.json`:
```json
{ "type": "carrossel", "title": "<tema>", "path": "output/carrosseis/<dir>/", "slides": N, "platform": "instagram", "created_at": "<ISO>" }
```

### 7. Resumo final

- Path do diretório
- "Para postar no Instagram: abra os PNGs na ordem `slide-01` até `slide-N`, suba no app de uma vez."
- "Para LinkedIn: faça upload do PDF no compositor de post."
- Sugestão de melhor horário de postagem baseado no nicho

## Tratamento de erro

Mesmo padrão da skill `criar-reel`: rate limit, auth, conteúdo bloqueado. Se 1 slide falhar, retente só ele 1x; se persistir, gere placeholder cinza com texto e marque o aluno.

## Não fazer

- Não use Puppeteer/HTML→PNG para o resultado final — qualidade insuficiente. Sempre Higgsfield.
- Não gere texto longo no slide (>50 palavras) — carrossel é visual.
- Não publique automaticamente.
