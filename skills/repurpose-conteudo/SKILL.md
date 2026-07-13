---
name: repurpose-conteudo
description: "Pega 1 vídeo longo (live, podcast, masterclass) e transforma em pacote multi-plataforma: 1 corte YouTube 8-15min + 3 Shorts/Reels + 1 carrossel + copys. Transcrição via ElevenLabs Scribe (preferido — free tier disponível, minutos variam por plano) com fallback automático para Whisper local. Claude identifica momentos virais, ffmpeg corta, skill `gerar-imagem` produz o carrossel. Use SEMPRE que o aluno disser: repurpose, transformar live, cortar masterclass, reaproveitar video, repurposing, transformar live em conteudo, reaproveitar gravacao, repurposar."
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
     - Extrair áudio com ffmpeg (mono 16k 64kbps) — limite real da API é 3GB (não 1GB)
     - POST https://api.elevenlabs.io/v1/speech-to-text com `curl -fS -w "%{http_code}"`
       multipart: file=<audio.mp3>, model_id="scribe_v1", language_code="por"
       header: xi-api-key: <chave>
     - Classificar status HTTP:
       · 200 → parsear `words`, agrupar em segments, salvar transcript.json (provider="elevenlabs-scribe")
       · 401/403 → "chave inválida ou sem permissão" → fallback Whisper
       · 429 → "limite atingido" → fallback Whisper (sem retry — limite é mensal)
       · 5xx ou timeout → retry uma vez após 5s; se persistir → fallback Whisper
       · qualquer outro → log do status + body[:200] → fallback Whisper
3. Whisper local (fallback ou single):
     - faster-whisper modelo "small" int8 via ~/.operacao-ia/tools/video-use/.venv/bin/python
     - **video_in passado via sys.argv[1]**, NUNCA interpolado em string Python (path pode ter aspas: `Cliente's live.mp4`)
     - Salvar transcript.json com provider="whisper-local"
```

**Implementação real (Python, NÃO pseudocódigo — copiar como referência):**

```python
import os, subprocess, json, time
from pathlib import Path

job_dir = Path.home() / ".operacao-ia/data/social-media/output/repurpose" / job_id
job_dir.mkdir(parents=True, exist_ok=True)
audio = job_dir / "audio.mp3"

# Extrair áudio compacto (mono 16k 64kbps) — reduz upload e cabe no limite de 3GB da API
subprocess.run([
    "ffmpeg", "-y", "-i", str(video_in),
    "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k",
    str(audio)
], check=True)

api_key = read_env("ELEVENLABS_API_KEY")
used_provider = None

def call_elevenlabs(audio_path, api_key, timeout=600):
    """Retorna (status_code: int, body: str). Usa curl com -w pra capturar HTTP code."""
    proc = subprocess.run([
        "curl", "-sS", "-X", "POST",
        "-w", "\\n__HTTP__%{http_code}",
        "--max-time", str(timeout),
        "https://api.elevenlabs.io/v1/speech-to-text",
        "-H", f"xi-api-key: {api_key}",
        "-F", f"file=@{audio_path}",
        "-F", "model_id=scribe_v1",
        "-F", "language_code=por",
        "-F", "diarize=false",
        "-F", "tag_audio_events=false",
    ], capture_output=True, text=True, timeout=timeout + 30)
    body, _, code = proc.stdout.rpartition("\n__HTTP__")
    try:
        return int(code), body
    except ValueError:
        return 0, proc.stdout  # curl falhou antes de receber resposta

def group_words_into_segments(words, gap=0.6):
    """Agrupa `words` (cada {text,start,end,type}) em segments por pausas > gap segundos.
    Filtra type='spacing' que a API insere entre palavras."""
    segments, cur, cur_start, last_end = [], [], None, 0.0
    for w in words:
        if w.get("type") == "spacing":
            continue
        if cur_start is None:
            cur_start = w["start"]
        if w["start"] - last_end > gap and cur:
            segments.append({"start": cur_start, "end": last_end, "text": " ".join(cur).strip()})
            cur, cur_start = [], w["start"]
        cur.append(w["text"])
        last_end = w["end"]
    if cur:
        segments.append({"start": cur_start, "end": last_end, "text": " ".join(cur).strip()})
    return segments

if api_key:
    try:
        status, body = call_elevenlabs(audio, api_key)
        # Retry uma vez em 5xx ou timeout
        if status >= 500 or status == 0:
            print(f"⚠️  ElevenLabs HTTP {status} — retry em 5s")
            time.sleep(5)
            status, body = call_elevenlabs(audio, api_key)

        if status == 200:
            data = json.loads(body)
            segments = group_words_into_segments(data.get("words", []))
            duration = data["words"][-1]["end"] if data.get("words") else 0
            (job_dir / "transcript.json").write_text(json.dumps({
                "provider": "elevenlabs-scribe",
                "duration": duration,
                "language": data.get("language_code", "por"),
                "segments": segments,
            }, ensure_ascii=False, indent=2))
            used_provider = "elevenlabs-scribe"
        elif status in (401, 403):
            print(f"❌ ElevenLabs {status}: chave inválida/sem permissão — fallback Whisper")
        elif status == 429:
            print(f"❌ ElevenLabs 429: limite mensal atingido — fallback Whisper")
        else:
            print(f"⚠️  ElevenLabs HTTP {status} — fallback Whisper. Body: {body[:200]}")
    except Exception as e:
        print(f"⚠️  ElevenLabs erro ({e}) — fallback Whisper")

if used_provider is None:
    # Whisper local — video_in via argv[1], NUNCA interpolado (paths podem ter aspas)
    py = Path.home() / ".operacao-ia/tools/video-use/.venv/bin/python"
    whisper_code = (
        "import json, sys\n"
        "from faster_whisper import WhisperModel\n"
        "m = WhisperModel('small', device='cpu', compute_type='int8')\n"
        "segs, info = m.transcribe(sys.argv[1], language='pt')\n"
        "out = [{'start': s.start, 'end': s.end, 'text': s.text.strip()} for s in segs]\n"
        "print(json.dumps({'provider':'whisper-local','duration':info.duration,'segments':out}, ensure_ascii=False))\n"
    )
    result = subprocess.run(
        [str(py), "-c", whisper_code, str(video_in)],
        check=True, capture_output=True, text=True
    )
    (job_dir / "transcript.json").write_text(result.stdout)
    used_provider = "whisper-local"

# Limpar áudio temporário (não precisa mais)
audio.unlink(missing_ok=True)
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
