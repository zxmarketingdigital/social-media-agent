#!/usr/bin/env python3
"""
Setup 7 — Etapa 5: Dashboard Local.
Gera ~/.operacao-ia/data/social-media/dashboard.html — calendário editorial + galeria.
"""
import json
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path.home() / ".operacao-ia" / "data" / "social-media"
MARCA = Path.home() / ".operacao-ia" / "config" / "marca.json"
DASHBOARD = DATA_DIR / "dashboard.html"
GALLERY = DATA_DIR / "gallery.json"

CADENCIA_SEMANAL = [
    ("Seg", "Reel",       "Hook didático sobre dor do público"),
    ("Ter", "Carrossel",  "5-7 slides: framework ou checklist"),
    ("Qua", "Reel",       "Bastidor + lição prática"),
    ("Qui", "Stories",    "Enquete + dica rápida + CTA"),
    ("Sex", "Reel",       "Case real ou prova social"),
    ("Sáb", "Longo",      "YouTube longo (8-15min) ou live"),
    ("Dom", "Carrossel",  "Resumo da semana ou inspiração"),
]


def load_marca():
    if not MARCA.exists():
        return {"nome": "Sua Marca", "nicho": "(definido na Etapa 1)", "tom": ""}
    try:
        return json.loads(MARCA.read_text())
    except Exception:
        return {"nome": "Sua Marca", "nicho": "", "tom": ""}


def init_gallery():
    if not GALLERY.exists():
        GALLERY.write_text(json.dumps({"items": []}, indent=2))


def calendario_html():
    rows = ""
    for dia, tipo, ideia in CADENCIA_SEMANAL:
        rows += f"<tr><td><strong>{dia}</strong></td><td>{tipo}</td><td>{ideia}</td></tr>\n"
    return rows


def render(marca):
    nome = marca.get("nome", "Sua Marca")
    nicho = marca.get("nicho", "")
    tom = marca.get("tom", "")
    today = date.today().strftime("%d/%m/%Y")

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{nome} · Social Media Agent</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{ --bg:#0f0f10; --fg:#eaeaea; --muted:#8a8a8a; --accent:#84cc16; --card:#1a1a1c; --border:#27272a; }}
  * {{ box-sizing:border-box }}
  body {{ margin:0; font-family:-apple-system, system-ui, sans-serif; background:var(--bg); color:var(--fg); line-height:1.5 }}
  header {{ padding:24px 32px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center }}
  h1 {{ margin:0; font-size:18px; font-weight:600 }}
  .meta {{ color:var(--muted); font-size:13px }}
  main {{ max-width:1200px; margin:0 auto; padding:32px }}
  section {{ background:var(--card); border:1px solid var(--border); border-radius:8px; padding:24px; margin-bottom:24px }}
  h2 {{ margin:0 0 16px; font-size:14px; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; color:var(--accent) }}
  table {{ width:100%; border-collapse:collapse }}
  th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--border); font-size:14px }}
  th {{ color:var(--muted); font-weight:500; font-size:12px; text-transform:uppercase; letter-spacing:0.5px }}
  tr:last-child td {{ border-bottom:none }}
  .empty {{ color:var(--muted); font-style:italic; padding:24px; text-align:center }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px }}
  .item {{ background:#0a0a0b; border:1px solid var(--border); border-radius:6px; padding:12px; font-size:13px }}
  .item .type {{ color:var(--accent); font-size:11px; text-transform:uppercase; margin-bottom:4px }}
  .commands {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px }}
  .cmd {{ background:#0a0a0b; border:1px solid var(--border); border-radius:6px; padding:12px 14px }}
  .cmd code {{ display:block; color:var(--accent); font-family:ui-monospace, monospace; font-size:13px; margin-bottom:4px }}
  .cmd small {{ color:var(--muted) }}
</style>
</head>
<body>
<header>
  <div>
    <h1>{nome}</h1>
    <div class="meta">{nicho}{' · ' + tom if tom else ''}</div>
  </div>
  <div class="meta">{today}</div>
</header>
<main>
  <section>
    <h2>Calendário Editorial — Cadência 3-2-1</h2>
    <table>
      <thead><tr><th>Dia</th><th>Formato</th><th>Ideia base</th></tr></thead>
      <tbody>{calendario_html()}</tbody>
    </table>
  </section>

  <section>
    <h2>Comandos Rápidos</h2>
    <div class="commands">
      <div class="cmd"><code>criar reel sobre [tópico]</code><small>Reel/Short 9:16 com avatar AI ou animação</small></div>
      <div class="cmd"><code>gerar carrossel 7 slides sobre [tema] para linkedin</code><small>5-10 slides + copy + imagens</small></div>
      <div class="cmd"><code>thumb yt: [título]</code><small>3 variantes de thumbnail 1280×720</small></div>
      <div class="cmd"><code>stories da semana</code><small>7 stories 9:16 com tema diário</small></div>
      <div class="cmd"><code>repurpose [caminho do vídeo]</code><small>Live longa → corte + Reels + carrossel + copy</small></div>
      <div class="cmd"><code>agente social</code><small>Menu com todas as opções</small></div>
    </div>
  </section>

  <section>
    <h2>Galeria — O que você já criou</h2>
    <div id="gallery"></div>
  </section>
</main>

<script>
async function loadGallery() {{
  try {{
    const res = await fetch('./gallery.json');
    const data = await res.json();
    const el = document.getElementById('gallery');
    if (!data.items || data.items.length === 0) {{
      el.innerHTML = '<div class="empty">Ainda vazio. Use os comandos acima e a galeria preenche automaticamente.</div>';
      return;
    }}
    const items = data.items.slice().reverse();
    el.innerHTML = '<div class="grid">' + items.map(i =>
      `<div class="item"><div class="type">${{i.type}}</div><div>${{i.title || i.path}}</div></div>`
    ).join('') + '</div>';
  }} catch(e) {{
    document.getElementById('gallery').innerHTML = '<div class="empty">Galeria vazia.</div>';
  }}
}}
loadGallery();
</script>
</body>
</html>
"""


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    init_gallery()
    marca = load_marca()
    DASHBOARD.write_text(render(marca))
    print(f"✅ Dashboard gerado: {DASHBOARD}")
    print("   Abra no browser: file://" + str(DASHBOARD))
    print("\nPronto para a Etapa 6 (demo de geração).")


if __name__ == "__main__":
    main()
