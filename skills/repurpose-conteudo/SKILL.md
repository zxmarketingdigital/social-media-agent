---
name: repurpose-conteudo
description: "Pega 1 vídeo longo (live, podcast, masterclass) e transforma em pacote multi-plataforma: 1 corte YouTube 8-15min + 3 Shorts/Reels + 1 carrossel + copys. Usa Whisper local (faster-whisper via video-use) para transcrever, Claude para identificar momentos virais, video-use para cortar, Higgsfield para imagens do carrossel. Use SEMPRE que o aluno disser: repurpose, transformar live, cortar masterclass, reaproveitar video, repurposing, transformar live em conteudo, reaproveitar gravacao, repurposar."
model: sonnet
effort: high
---

# Repurpose de Conteúdo

Transforma 1 vídeo longo em pacote multi-plataforma. O fluxo é demorado (~15-25min) e custa principalmente pelas gerações Higgsfield do carrossel.

## Pré-requisitos

- `~/.operacao-ia/tools/video-use/` instalado (Etapa 3 do Setup)
- ffmpeg no PATH
- MCP Higgsfield conectado
- `marca.json` e `DESIGN.md` preenchidos

Se faltar algo, oriente o aluno antes de prosseguir.

## Inputs

1. **Caminho do vídeo de entrada** — ex: `~/Downloads/zoom-meeting.mp4`
2. **Duração do corte longo** — `8min`, `12min`, `15min`. Default: `12min`
3. **Quantidade de Shorts/Reels** — 1 a 5. Default: 3
4. **Carrossel** — gerar carrossel também? `sim`/`não`. Default: `sim`

## Fluxo

### 1. Transcrever com Whisper local

Use o venv do video-use:

```bash
~/.operacao-ia/tools/video-use/.venv/bin/python -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
segments, info = model.transcribe('{caminho_video}', language='pt')
import json, sys
out = [{'start': s.start, 'end': s.end, 'text': s.text.strip()} for s in segments]
print(json.dumps({'duration': info.duration, 'segments': out}, ensure_ascii=False))
" > ~/.operacao-ia/data/social-media/output/repurpose/{job_id}/transcript.json
```

Substitua `{caminho_video}` e `{job_id}` (timestamp + slug do arquivo).

Tempo esperado: ~1/3 a 1/2 da duração do vídeo em Mac M1+; até 1x em Intel.

### 2. Identificar momentos virais

Leia o transcript. Identifique:

- **1 segmento de 8-15min** que funciona como corte standalone com começo-meio-fim. Critério: tem hook claro, desenvolve uma ideia, fecha com aprendizado/CTA.
- **N momentos curtos (15-60s)** com punchline, frase de impacto ou virada — viram Shorts/Reels.
- **3-7 pontos chave** que sintetizam a discussão — viram o carrossel.

Use Claude para esta análise. Apresente as escolhas ao aluno e peça aprovação antes de cortar.

### 3. Cortar com video-use

Para cada clip:

```bash
ffmpeg -i {caminho_video} -ss {start_sec} -to {end_sec} \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 128k \
  output/repurpose/{job_id}/longo-12min.mp4
```

Para os Shorts/Reels (9:16), recorte vertical com crop centralizado:

```bash
ffmpeg -i {caminho_video} -ss {start_sec} -to {end_sec} \
  -vf "crop=ih*9/16:ih,scale=1080:1920" \
  -c:v libx264 -preset medium -crf 20 \
  -c:a aac -b:a 128k \
  output/repurpose/{job_id}/short-{N}.mp4
```

Se o video-use já tem helpers melhores em `~/.operacao-ia/tools/video-use/helpers/`, prefira eles.

### 4. Gerar legendas/copys

Para cada clip gere:
- Título sugerido (YouTube longo: SEO-friendly; Shorts/Reels: hook curto)
- Descrição (YouTube longo: 150-300 palavras com cap. principais)
- Caption Instagram/TikTok (curta + hashtags)

Salve em `output/repurpose/{job_id}/copys/`.

### 5. Gerar carrossel (se solicitado)

Invoque a skill `gerar-carrossel` passando como tema "Principais lições de {nome_do_video}" e os 3-7 pontos extraídos. Output vai para `output/repurpose/{job_id}/carrossel/`.

### 6. Estrutura final

```
output/repurpose/{job_id}/
  transcript.json
  longo-12min.mp4
  short-1.mp4
  short-2.mp4
  short-3.mp4
  carrossel/
    slide-01-capa.png
    ...
  copys/
    longo.txt
    short-1.txt
    short-2.txt
    short-3.txt
    carrossel.txt
  RESUMO.md   # navegação do pacote
```

### 7. Atualizar galeria

Leia `~/.operacao-ia/data/social-media/gallery.json`, append 1 item agregado em `data["items"]`, escreva de volta:
```json
{ "type": "repurpose", "title": "<nome>", "path": "output/repurpose/{job_id}/", "count": { "longo": 1, "shorts": 3, "carrossel": 1 }, "created_at": "<ISO>" }
```

### 8. Resumo final ao aluno

- Resumo do que foi gerado (paths + duração de cada arquivo)
- Sugestão de ordem de publicação (longo → 1 Short por dia → carrossel no fechamento)
- Tempo total de processamento

## Tratamento de erro

- **Whisper falha:** verificar se o áudio existe (`ffprobe`). Pode ser arquivo corrompido. Sugerir re-encode com `ffmpeg -i input.mp4 -c:v copy -c:a aac fixed.mp4`.
- **Higgsfield rate limit no carrossel:** segue lógica da skill `gerar-carrossel`.
- **Corte cai em meio de frase:** ajustar `start`/`end` pra word-boundaries usando o transcript.

## Não fazer

- Não envie áudio pra ElevenLabs ou outra API paga — Whisper local resolve.
- Não rode Whisper na CPU em modelo `large` sem confirmar com aluno — pode levar horas.
- Não publique automaticamente.
