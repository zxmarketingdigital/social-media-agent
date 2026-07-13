# Graph Report - .  (2026-05-14)

## Corpus Check
- Corpus is ~17,066 words - fits in a single context window. You may not need a graph.

## Summary
- 129 nodes · 213 edges · 15 communities detected
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Cluster 0|Cluster 0]]
- [[_COMMUNITY_Cluster 1|Cluster 1]]
- [[_COMMUNITY_Cluster 2|Cluster 2]]
- [[_COMMUNITY_Cluster 3|Cluster 3]]
- [[_COMMUNITY_Cluster 4|Cluster 4]]
- [[_COMMUNITY_Cluster 5|Cluster 5]]
- [[_COMMUNITY_Cluster 6|Cluster 6]]
- [[_COMMUNITY_Cluster 7|Cluster 7]]
- [[_COMMUNITY_Cluster 8|Cluster 8]]
- [[_COMMUNITY_Cluster 9|Cluster 9]]
- [[_COMMUNITY_Cluster 10|Cluster 10]]
- [[_COMMUNITY_Cluster 11|Cluster 11]]
- [[_COMMUNITY_Cluster 12|Cluster 12]]
- [[_COMMUNITY_Cluster 13|Cluster 13]]
- [[_COMMUNITY_Cluster 14|Cluster 14]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 12 edges
2. `Repurpose Conteúdo` - 12 edges
3. `Criar Reel` - 11 edges
4. `run()` - 10 edges
5. `Gerar Carrossel` - 10 edges
6. `Agente Social Media` - 9 edges
7. `Criar Thumbnail` - 8 edges
8. `Gerar Imagem (Helper)` - 8 edges
9. `Gerar Vídeo MP4 (Helper)` - 8 edges
10. `DESIGN.md (Brand Design System)` - 8 edges

## Surprising Connections (you probably didn't know these)
- `resize_png()` --calls--> `run()`  [INFERRED]
  skills/gerar-imagem/scripts/gerar.py → setup/setup_transcricao.py
- `gen_image2()` --calls--> `run()`  [INFERRED]
  skills/gerar-imagem/scripts/gerar.py → setup/setup_transcricao.py
- `setup_marca.py (Etapa 1)` --produces--> `marca.json`  [EXTRACTED]
  CLAUDE.md → skills/criar-reel/SKILL.md
- `setup_demo.py (Etapa 6)` --calls--> `Criar Reel`  [EXTRACTED]
  CLAUDE.md → skills/criar-reel/SKILL.md
- `setup_demo.py (Etapa 6)` --calls--> `Gerar Carrossel`  [EXTRACTED]
  CLAUDE.md → skills/gerar-carrossel/SKILL.md

## Communities

### Community 0 - "Cluster 0"
Cohesion: 0.15
Nodes (26): Agente Social Media, config.json (Phase Tracking), Criar Reel, Criar Thumbnail, dashboard.html (Local Dashboard), elevenlabs.env (API Key Store), ElevenLabs Scribe, gallery.json (+18 more)

### Community 1 - "Cluster 1"
Cohesion: 0.2
Nodes (16): check_bun(), check_chrome(), check_claude_cli(), check_codex_or_chatgpt_cli(), check_ffmpeg(), check_gh(), check_higgsfield_mcp(), check_prior_setup() (+8 more)

### Community 2 - "Cluster 2"
Cohesion: 0.26
Nodes (13): clone_or_pull(), ler_chave_existente(), main(), prompt(), Retorna True se faster_whisper importa OK, False caso contrário., Bate em GET /v1/user — se 200, chave válida., Apaga o arquivo elevenlabs.env se existir — chamado quando o aluno     decide nã, remover_chave_antiga() (+5 more)

### Community 3 - "Cluster 3"
Cohesion: 0.33
Nodes (9): copy_template(), emit_custom_marker(), emit_showcase_instructions(), main(), pick_choice(), Quando o aluno escolhe 'custom', cria um arquivo placeholder e instrui o Claude, Imprime instruções para o Claude gerar o design-showcase.html adaptado     à mar, show_options() (+1 more)

### Community 4 - "Cluster 4"
Cohesion: 0.22
Nodes (10): Bun Runtime, Chrome Headless (puppeteer-core), Codex CLI, ffmpeg, Gerar Vídeo MP4 (Helper), Higgsfield AI MCP, render.mjs (Puppeteer Script), scene.html (Animation Source) (+2 more)

### Community 5 - "Cluster 5"
Cohesion: 0.44
Nodes (8): gen_gemini(), gen_image2(), load_env_key(), log(), main(), Generate via Google GenAI — gemini-* usa :generateContent, imagen-* usa :predict, Generate via Codex CLI built-in image_gen tool (gpt-image-2)., resize_png()

### Community 6 - "Cluster 6"
Cohesion: 0.43
Nodes (7): dark-mono Design Template, DESIGN.md (Brand Design System), design-showcase.html (Visual Approval), design-showcase-template.html (785 lines), light-editorial Design Template, setup_design_system.py (Etapa 2), vivid-pop Design Template

### Community 7 - "Cluster 7"
Cohesion: 0.6
Nodes (5): calendario_html(), init_gallery(), load_marca(), main(), render()

### Community 8 - "Cluster 8"
Cohesion: 0.7
Nodes (4): has_chrome(), has_codex_logged_in(), has_gemini_key(), main()

### Community 9 - "Cluster 9"
Cohesion: 0.6
Nodes (4): dirs_equal(), main(), print_skills_explainer(), Imprime o que cada skill faz, quando usar, trigger e comando exemplo.

### Community 10 - "Cluster 10"
Cohesion: 0.7
Nodes (4): main(), mark_phase(), open_dashboard(), show_summary()

### Community 11 - "Cluster 11"
Cohesion: 0.6
Nodes (5): gemini.env (API Key Store), Gemini Nano Banana (gemini-3.1-flash-image-preview), Gerar Imagem (Helper), gpt-image-2 (OpenAI), Imagen 4 Ultra

### Community 12 - "Cluster 12"
Cohesion: 0.4
Nodes (5): Bunny CDN (Video Hosting), MasterClass Setup 7 (Video), upload-aulas-hub Skill, Cloudflare Pages Deploy (wrangler), ZX Control Área de Membros

### Community 13 - "Cluster 13"
Cohesion: 0.83
Nodes (3): ask(), main(), pick_tom()

### Community 14 - "Cluster 14"
Cohesion: 1.0
Nodes (1): Workflow 3-2-1 (Weekly Cadence)

## Knowledge Gaps
- **30 isolated node(s):** `Verifica higgsfield MCP. NÃO bloqueia (geração de vídeo agora é via gerar-video-`, `Image gen preferida usa gpt-image-2 via Codex CLI (login ChatGPT). Não bloqueia.`, `gerar-video-mp4 usa Chrome headless via puppeteer. Não bloqueia.`, `gerar-video-mp4 usa puppeteer-core via Bun. Não bloqueia.`, `Imprime o que cada skill faz, quando usar, trigger e comando exemplo.` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Cluster 14`** (1 nodes): `Workflow 3-2-1 (Weekly Cadence)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.