---
name: criar-reel
description: "Gera Reel/Short/TikTok 9:16 (ou Reel feed 4:5) com hook + corpo + CTA. Usa Higgsfield AI para gerar o vídeo (avatar AI opcional) lendo marca.json e DESIGN.md para manter identidade. Use SEMPRE que o aluno disser: criar reel, novo reel, gerar reel, reel sobre, criar shorts, novo shorts, criar tiktok, video curto, reel instagram, criativo reels."
model: sonnet
effort: medium
---

# Criar Reel/Short/TikTok

Skill para gerar 1 vídeo vertical curto pronto pra publicar no Instagram Reels, TikTok ou YouTube Shorts.

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
4. **Aspect ratio** — `9:16` (default) ou `4:5` (feed)
5. **Avatar AI?** — `sim`/`não`. Default: `sim` (usa Higgsfield avatar). Se `não`, gera Reel animado com texto + b-roll AI.

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

### 2. Geração via Higgsfield

Após aprovação, chame as tools do MCP Higgsfield (`mcp__higgsfield__*`).

**Se avatar AI = sim:**
- Tool a usar: `generate_avatar_video` (ou equivalente — confira tools disponíveis em `claude mcp list` ou tente `generate_video` com parâmetro `avatar=true`)
- Parâmetros:
  - `script`: o roteiro completo (hook + corpo + CTA), formatado pro avatar falar
  - `aspect_ratio`: conforme escolha
  - `duration_seconds`: conforme escolha
  - `style_prompt`: prompt visual baseado em DESIGN.md (extrair seção "Para Higgsfield")
  - `voice`: pedir preferência do aluno (masculina/feminina/neutra) — default neutra

**Se avatar AI = não:**
- Tool: `generate_video` (ou similar)
- Parâmetros:
  - `prompt`: descrição visual do Reel (b-roll genérico relacionado ao tema + texto on-screen com o roteiro)
  - `aspect_ratio`, `duration_seconds`, `style_prompt` idem

### 3. Output

Salve em:
```
~/.operacao-ia/data/social-media/output/reels/YYYY-MM-DD_<slug-do-tema>.mp4
~/.operacao-ia/data/social-media/output/reels/YYYY-MM-DD_<slug-do-tema>.copy.txt
```

Onde `<slug-do-tema>` é o tema em kebab-case (`como-usar-ia-no-atendimento`).

`.copy.txt` contém:
- Roteiro completo
- Legenda sugerida pra postagem (chame a skill `gerar-copy-post` internamente se quiser)
- Hashtags sugeridas (8-12, mix de nicho + amplas)

### 4. Atualizar galeria

Append em `~/.operacao-ia/data/social-media/gallery.json`:

```json
{
  "items": [
    { "type": "reel", "title": "<tema>", "path": "output/reels/...", "created_at": "<ISO>" }
  ]
}
```

(Leia o JSON, append no array `items`, escreva de volta.)

### 5. Resumo final

Mostre ao aluno:
- Path do MP4 gerado
- Path do copy
- Sugestão de horário pra publicar baseado no nicho (manhã pra B2B, fim de tarde pra B2C)
- Comando pra abrir no Finder: `open ~/.operacao-ia/data/social-media/output/reels/`

## Tratamento de erro Higgsfield

- **Rate limit:** mostre mensagem clara ("Higgsfield atingiu o limite — tente em 5min ou faça upgrade do plano"). Não tente retry automático mais de 1x.
- **Auth expirou:** instrua `claude mcp` re-login.
- **Tool não encontrada:** liste as tools disponíveis com `claude mcp list` e adapte o nome no próximo retry.
- **Conteúdo bloqueado:** revise o prompt removendo termos sensíveis e tente de novo.

## Não fazer

- Não use Puppeteer, ffmpeg, ou qualquer engine local para o vídeo final — sempre Higgsfield.
- Não suba pra YouTube/IG/TikTok automaticamente — esse Setup é manual.
- Não invente API keys — Higgsfield autentica via MCP no Claude Code.
