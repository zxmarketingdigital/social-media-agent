# MasterClass Setup 7 — Roteiro do Vídeo

Vídeo único (aula MasterClass) que apresenta todo o Setup. Será hospedado no Bunny e exibido em `panel-s7-0` da área de membros do ZX Control.

**Duração-alvo:** 12-18 minutos.

## Estrutura

### 1. Abertura (0:00 - 1:30)
- Contexto: aluno já tem agente de tráfego (Setup 6) → agora precisa alimentar funil orgânico
- Promessa: ao final, criar Reel + carrossel + thumb sem editor de vídeo, sem designer, sem ficar travado em frente à tela em branco
- Princípio: Setup 7 é sobre CRIAR — publicação fica manual (você decide quando e onde postar)

### 2. Quem deve usar (1:30 - 2:30)
- Criador solo / personal brand
- Quem tem 4 plataformas pra alimentar e não tem tempo
- Quem quer manter consistência visual sem virar designer

### 3. Demo ao vivo (2:30 - 9:00)
Mostrar 3 comandos em sequência:

- `criar reel sobre [tema do nicho do criador]` — gerar com avatar AI, mostrar output
- `gerar carrossel 7 slides sobre [tema] para linkedin` — mostrar copy + imagens AI
- `thumb yt: [título]` — 3 variantes

Comentar enquanto roda: como o `DESIGN.md` mantém consistência, como o `marca.json` define a voz, custo aproximado por geração.

### 4. Workflow semanal sugerido (9:00 - 12:00)
- Cadência 3-2-1: 3 Reels + 2 carrosséis + 1 longo (YouTube)
- Stories diárias usando o pack semanal
- Repurpose 1x por mês de uma live longa

### 5. Setup explicado em alto nível (12:00 - 15:00)
- 8 etapas, ~30min total
- O que cada etapa configura
- Pré-requisitos: Setups 1-6 + Higgsfield AI (conta grátis ou paga)

### 6. Custos & expectativas (15:00 - 17:00)
- Higgsfield: estimativa de uso intenso (~5 Reels + 2 repurposes/sem)
- Whisper local = grátis (CPU)
- Tempo de geração realista (não é instantâneo)

### 7. CTA (17:00 - 18:00)
- Instalar agora
- Próximos setups
- Comunidade

## Notas de produção

- Gravar com fundo `DESIGN.md dark-mono` pra demonstrar o sistema
- Mostrar a tela do Claude Code com font legível (zoom in)
- Banner ZX LAB sutil no canto superior direito (consistente com cortes-masterclass)
- Áudio limpo (acompressor + highshelf + loudnorm conforme `feedback_youtube_cortes_masterclass`)

## Upload

Após gravação, usar skill `upload-aulas-hub` ou processo manual:
1. Subir MP4 no Bunny (lib `MasterClass ZX Control`)
2. Pegar GUID
3. Substituir `BUNNY_GUID_S7` em `~/projetos/zx-control-semana1/docs/area-membros.html`
4. Deploy área de membros: `wrangler pages deploy ~/projetos/zx-control-semana1/docs/ --project-name zx-control-semana1`
