---
name: repurpose-conteudo
description: "Pega 1 vídeo longo (live, podcast, masterclass) e transforma em pacote multi-plataforma: 1 corte YouTube 8-15min + 3 Shorts/Reels + 1 carrossel + copys. Transcrição via ElevenLabs Scribe (preferido — free tier ~10h/mês) com fallback automático para Whisper local. Claude identifica momentos virais, ffmpeg corta, skill `gerar-imagem` produz o carrossel. Use SEMPRE que o aluno disser: repurpose, transformar live, cortar masterclass, reaproveitar video, repurposing, transformar live em conteudo, reaproveitar gravacao, repurposar."
model: sonnet
effort: high
---

# Repurpose de Conteúdo

Transforma 1 vídeo longo em pacote multi-plataforma. Fluxo demorado (~10-20min com ElevenLabs, ~25-40min só com Whisper local).

## Pré-requisitos

- Etapa 3 do Setup concluída (Whisper local OBRIGATÓRIO como fallback; ElevenLabs OPCIONAL mas recomendado)
- ffmpeg no PATH
- `marca.json` e `DESIGN.md` preenchidos
- Codex CLI logado OU `GEMINI_API_KEY` configurado (para `gerar-imagem` montar carrossel) — Higgsfield MCP é fallback adicional

Se faltar algo, oriente o aluno antes de prosseguir.

## Inputs

1. **Caminho do vídeo de entrada** — ex: `~/Downloads/zoom-meeting.mp4`
2. **Duração do corte longo** — `8min`, `12min`, `15min`. Default: `12min`
3. **Quantidade de Shorts/Reels** — 1 a 5. Default: 3
4. **Carrossel** — gerar carrossel também? `sim`/`não`. Default: `sim`

## Fluxo

### 1. Transcrever — ElevenLabs Scribe (preferred) com fallback automático para Whisper

**Pseudocódigo do roteamento (implementar inline):**

```
1. Ler ELEVENLABS_API_KEY de ~/.operacao-ia/config/elevenlabs.env (ou env var)
2. Se chave existe → tentar ElevenLabs:
     - Extrair áudio com ffmpeg se vídeo > 1GB (POST /v1/speech-to-text aceita até 1GB)
     - POST https://api.elevenlabs.io/v1/speech-to-text
       multipart: file=<audio.mp3>, model_id="scribe_v1", language_code="por"
       header: xi-api-key: <chave>
     - Sucesso → parsear `words` em segments {start, end, text}, salvar transcript.json, marcar provider="elevenlabs"
     - Erro 401 (chave inválida) ou 429 (limite atingido) ou outro → log claro + cair para Whisper
3. Whisper local (fallback ou single):
     - faster-whisper modelo "small" int8 via ~/.operacao-ia/tools/video-use/.venv/bin/python
     - Salvar transcript.json com provider="whisper-local"
```

**Comando ElevenLabs (curl, em pseudocódigo Python):**

```python
import os, subprocess, json, urllib.request
from pathlib import Path

job_dir = Path.home() / ".operacao-ia/data/social-media/output/repurpose" / job_id
job_dir.mkdir(parents=True, exist_ok=True)
audio = job_dir / "audio.mp3"

# Extrair áudio compacto pra reduzir upload
subprocess.run([
    "ffmpeg", "-y", "-i", str(video_in),
    "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
    str(audio)
], check=True)

api_key = read_env("ELEVENLABS_API_KEY")
if api_key:
    try:
        # Use requests/curl via subprocess para multipart simples
        result = subprocess.run([
            "curl", "-sS", "-X", "POST",
            "https://api.elevenlabs.io/v1/speech-to-text",
            "-H", f"xi-api-key: {api_key}",
            "-F", f"file=@{audio}",
            "-F", "model_id=scribe_v1",
            "-F", "language_code=por",
            "-F", "diarize=false",
            "-F", "tag_audio_events=false",
        ], capture_output=True, text=True, check=True, timeout=600)
        data = json.loads(result.stdout)
        # data["words"]: lista de {text, start, end, type}
        # Agrupar em segmentos por pausas > 0.6s
        segments = group_words_into_segments(data["words"])
        (job_dir / "transcript.json").write_text(json.dumps({
            "provider": "elevenlabs-scribe",
            "duration": data.get("language_probability", 0) and data["words"][-1]["end"],
            "language": data.get("language_code", "por"),
            "segments": segments,
        }, ensure_ascii=False, indent=2))
        used_provider = "elevenlabs-scribe"
    except Exception as e:
        print(f"⚠️  ElevenLabs falhou ({e}) — caindo para Whisper local")
        api_key = None  # força fallback

if not api_key:
    # Whisper local
    py = Path.home() / ".operacao-ia/tools/video-use/.venv/bin/python"
    subprocess.run([str(py), "-c", f"""
import json
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8')
segs, info = m.transcribe('{video_in}', language='pt')
out = [{{'start': s.start, 'end': s.end, 'text': s.text.strip()}} for s in segs]
print(json.dumps({{'provider':'whisper-local','duration':info.duration,'segments':out}}, ensure_ascii=False))
"""], check=True, stdout=open(job_dir / "transcript.json", "w"))
    used_provider = "whisper-local"

print(f"✅ Transcrição: {used_provider}")
```

**Timings esperados (1h de áudio):**
- ElevenLabs Scribe: ~2-4min (depende de upload)
- Whisper small int8 num M1: ~15-25min
- Whisper small int8 num Intel: ~40-60min

Mostre o tempo + provider ao aluno após a transcrição.

### 2. Identificar momentos virais

Leia o transcript. Identifique:

- **1 segmento de 8-15min** que funciona como corte standalone com começo-meio-fim. Critério: tem hook claro, desenvolve uma ideia, fecha com aprendizado/CTA.
- **N momentos curtos (15-60s)** com punchline, frase de impacto ou virada — viram Shorts/Reels.
- **3-7 pontos chave** que sintetizam a discussão — viram o carrossel.

Use Claude para esta análise. Apresente as escolhas ao aluno e peça aprovação antes de cortar.

### 3. Cortar com ffmpeg

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

Invoque a skill `gerar-carrossel` passando como tema "Principais lições de {nome_do_video}" e os 3-7 pontos extraídos. A própria `gerar-carrossel` usa `gerar-imagem` (gpt-image-2 → Gemini Nano Banana → Imagen 4). Output vai para `output/repurpose/{job_id}/carrossel/`.

### 6. Estrutura final

```
output/repurpose/{job_id}/
  transcript.json   # inclui campo "provider": "elevenlabs-scribe" ou "whisper-local"
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
  RESUMO.md   # navegação do pacote + provider de transcrição usado
```

### 7. Atualizar galeria

Leia `~/.operacao-ia/data/social-media/gallery.json`, append 1 item agregado em `data["items"]`, escreva de volta:
```json
{ "type": "repurpose", "title": "<nome>", "path": "output/repurpose/{job_id}/",
  "count": { "longo": 1, "shorts": 3, "carrossel": 1 },
  "transcription_provider": "elevenlabs-scribe",
  "created_at": "<ISO>" }
```

### 8. Resumo final ao aluno

- Resumo do que foi gerado (paths + duração de cada arquivo)
- Provider de transcrição usado (ElevenLabs/Whisper) + tempo gasto
- Sugestão de ordem de publicação (longo → 1 Short por dia → carrossel no fechamento)
- Tempo total de processamento

## Tratamento de erro

- **ElevenLabs 401:** chave inválida — apagar `elevenlabs.env` ou rodar `setup_transcricao.py` de novo.
- **ElevenLabs 429:** limite mensal atingido — cair pra Whisper automático, avisar aluno.
- **Whisper falha:** verificar áudio (`ffprobe`). Arquivo pode estar corrompido. Sugerir re-encode com `ffmpeg -i input.mp4 -c:v copy -c:a aac fixed.mp4`.
- **Carrossel rate limit:** segue lógica de `gerar-carrossel`/`gerar-imagem`.
- **Corte cai em meio de frase:** ajustar `start`/`end` para word-boundaries usando o transcript (palavras com timestamps).

## Não fazer

- Não pular o fallback — se ElevenLabs falhar, Whisper local DEVE rodar (skill não pode quebrar por falta de chave paga).
- Não rode Whisper na CPU em modelo `large` sem confirmar com aluno — pode levar horas.
- Não publique automaticamente.
- Não envie áudio pra outras APIs pagas sem perguntar (ElevenLabs free tier já cobre o uso típico).
