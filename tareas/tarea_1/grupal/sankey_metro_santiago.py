"""
Sankey Dinámico - Metro de Santiago (2010-2025)
Flujo: Año → Líneas → Tipo de Pago
Fuente: Metro S.A. — Tabla A18 (afluencia por línea) y Tabla A19 (transacciones por tipo de tarifa)
"""

import json

# ── Datos ───────────────────────────────────────────────────────────────────────

LINE_DATA = {
    2010: {"Línea 1": 259.500, "Línea 2": 122.302, "Línea 4": 115.667, "Línea 4A": 19.028, "Línea 5": 104.220},
    2011: {"Línea 1": 252.687, "Línea 2": 120.241, "Línea 4": 115.598, "Línea 4A": 18.254, "Línea 5": 133.160},
    2012: {"Línea 1": 257.510, "Línea 2": 118.650, "Línea 4": 117.201, "Línea 4A": 18.932, "Línea 5": 136.442},
    2013: {"Línea 1": 263.633, "Línea 2": 121.853, "Línea 4": 120.105, "Línea 4A": 19.631, "Línea 5": 141.654},
    2014: {"Línea 1": 261.952, "Línea 2": 121.909, "Línea 4": 119.417, "Línea 4A": 20.289, "Línea 5": 144.081},
    2015: {"Línea 1": 257.416, "Línea 2": 118.762, "Línea 4": 119.792, "Línea 4A": 20.627, "Línea 5": 144.575},
    2016: {"Línea 1": 260.993, "Línea 2": 121.102, "Línea 4": 120.236, "Línea 4A": 20.803, "Línea 5": 146.938},
    2017: {"Línea 1": 270.647, "Línea 2": 122.971, "Línea 4": 118.825, "Línea 4A": 20.399, "Línea 5": 146.761, "Línea 6":   5.461},
    2018: {"Línea 1": 278.072, "Línea 2": 121.250, "Línea 4": 118.935, "Línea 4A": 19.969, "Línea 5": 143.668, "Línea 6":  39.112},
    2019: {"Línea 1": 262.687, "Línea 2": 102.893, "Línea 3":  55.821, "Línea 4": 101.894, "Línea 4A": 16.536, "Línea 5": 123.100, "Línea 6": 40.742},
    2020: {"Línea 1":  93.241, "Línea 2":  43.180, "Línea 3":  27.339, "Línea 4":  37.797, "Línea 4A":  5.944, "Línea 5":  39.424, "Línea 6": 16.433},
    2021: {"Línea 1": 118.420, "Línea 2":  54.334, "Línea 3":  36.914, "Línea 4":  53.574, "Línea 4A":  9.515, "Línea 5":  64.891, "Línea 6": 21.720},
    2022: {"Línea 1": 186.706, "Línea 2":  77.399, "Línea 3":  56.138, "Línea 4":  78.776, "Línea 4A": 13.509, "Línea 5":  97.981, "Línea 6": 33.904},
    2023: {"Línea 1": 206.730, "Línea 2":  84.740, "Línea 3":  63.040, "Línea 4":  87.130, "Línea 4A": 14.900, "Línea 5": 104.340, "Línea 6": 38.210},
    2024: {"Línea 1": 217.332, "Línea 2":  96.135, "Línea 3":  74.250, "Línea 4":  92.491, "Línea 4A": 14.077, "Línea 5": 108.325, "Línea 6": 37.445},
    2025: {"Línea 1": 186.008, "Línea 2":  80.668, "Línea 3":  63.845, "Línea 4":  79.506, "Línea 4A": 11.878, "Línea 5":  91.840, "Línea 6": 34.383},
}

FARE_DATA = {
    2010: {"Adulto": 447_988_358, "Estud. media/sup.": 158_312_465, "Estud. básica": 10_075_753, "Adulto Mayor":          0},
    2011: {"Adulto": 452_696_574, "Estud. media/sup.": 174_869_913, "Estud. básica": 11_763_981, "Adulto Mayor":          0},
    2012: {"Adulto": 454_752_496, "Estud. media/sup.": 181_143_307, "Estud. básica": 12_913_027, "Adulto Mayor":          0},
    2013: {"Adulto": 466_288_296, "Estud. media/sup.": 187_497_318, "Estud. básica": 13_884_720, "Adulto Mayor":          0},
    2014: {"Adulto": 466_758_448, "Estud. media/sup.": 187_680_898, "Estud. básica": 14_293_328, "Adulto Mayor":          0},
    2015: {"Adulto": 460_270_442, "Estud. media/sup.": 189_344_575, "Estud. básica": 12_195_440, "Adulto Mayor":          0},
    2016: {"Adulto": 466_432_899, "Estud. media/sup.": 192_849_610, "Estud. básica": 12_665_007, "Adulto Mayor":          0},
    2017: {"Adulto": 483_011_334, "Estud. media/sup.": 188_335_611, "Estud. básica": 14_838_491, "Adulto Mayor":          0},
    2018: {"Adulto": 517_898_622, "Estud. media/sup.": 183_713_585, "Estud. básica": 18_562_948, "Adulto Mayor":          0},
    2019: {"Adulto": 502_378_894, "Estud. media/sup.": 178_920_406, "Estud. básica": 22_403_352, "Adulto Mayor":          0},
    2020: {"Adulto": 199_917_287, "Estud. media/sup.":  41_124_767, "Estud. básica": 11_026_529, "Adulto Mayor": 11_295_692},
    2021: {"Adulto": 281_032_559, "Estud. media/sup.":  45_984_136, "Estud. básica": 11_849_548, "Adulto Mayor": 20_501_174},
    2022: {"Adulto": 354_929_315, "Estud. media/sup.": 106_531_711, "Estud. básica": 21_471_504, "Adulto Mayor": 35_708_527},
    2023: {"Adulto": 403_632_229, "Estud. media/sup.": 120_497_588, "Estud. básica": 26_654_190, "Adulto Mayor": 48_306_384},
    2024: {"Adulto": 422_692_176, "Estud. media/sup.": 128_454_831, "Estud. básica": 30_892_084, "Adulto Mayor": 58_019_754},
    2025: {"Adulto": 428_204_174, "Estud. media/sup.": 134_617_525, "Estud. básica": 32_212_897, "Adulto Mayor": 65_952_087},
}

LINE_COLORS = {
    "Línea 1":  "#C13B3B",
    "Línea 2":  "#D4863A",
    "Línea 3":  "#7A5C2E",
    "Línea 4":  "#3A5FA0",
    "Línea 4A": "#6A8BC4",
    "Línea 5":  "#2E8B57",
    "Línea 6":  "#7B3FA0",
}

FARE_COLORS = {
    "Adulto":            "#378ADD",
    "Estud. media/sup.": "#1D9E75",
    "Estud. básica":     "#BA7517",
    "Adulto Mayor":      "#D4537E",
}

YEARS = list(range(2010, 2026))
ALL_LINES = ["Línea 1", "Línea 2", "Línea 3", "Línea 4", "Línea 4A", "Línea 5", "Línea 6"]
ALL_FARES = ["Adulto", "Estud. media/sup.", "Estud. básica", "Adulto Mayor"]


# ── Helpers ──────────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)

def rgba(hex_color, alpha):
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"

def fmt_m(val_m):
    return f"{val_m:.1f}M"

def build_year_data(year):
    lines = LINE_DATA[year]
    fares = {k: v for k, v in FARE_DATA[year].items() if v > 0}
    line_names = sorted(lines.keys(), key=lambda k: -lines[k])
    fare_names = [f for f in ALL_FARES if f in fares]
    total_line = sum(lines.values())
    total_fare = sum(fares.values())

    node_labels = [str(year)] + line_names + fare_names
    node_customdata = [""]
    for ln in line_names:
        pct = lines[ln] / total_line * 100
        node_customdata.append(f"{fmt_m(lines[ln])} ({pct:.1f}%)")
    for fn in fare_names:
        val_m = fares[fn] / 1e6
        pct = fares[fn] / total_fare * 100
        node_customdata.append(f"{fmt_m(val_m)} ({pct:.1f}%)")

    node_colors = ["#555550"]
    node_colors += [LINE_COLORS.get(n, "#888") for n in line_names]
    node_colors += [FARE_COLORS.get(n, "#888") for n in fare_names]

    year_idx = 0
    line_idx = {n: i + 1 for i, n in enumerate(line_names)}
    fare_idx = {n: len(line_names) + 1 + i for i, n in enumerate(fare_names)}

    sources, targets, values, link_colors = [], [], [], []

    for ln in line_names:
        sources.append(year_idx)
        targets.append(line_idx[ln])
        values.append(round(lines[ln], 3))
        link_colors.append(rgba(LINE_COLORS.get(ln, "#888"), 0.5))

    for ln in line_names:
        line_share = lines[ln] / total_line
        for fn in fare_names:
            fare_share = fares[fn] / total_fare
            val = line_share * fare_share * total_line
            sources.append(line_idx[ln])
            targets.append(fare_idx[fn])
            values.append(round(val, 3))
            link_colors.append(rgba(LINE_COLORS.get(ln, "#888"), 0.28))

    leaders = sorted(lines.keys(), key=lambda k: -lines[k])[:2]

    return {
        "total":           round(total_line, 1),
        "n_lines":         len(lines),
        "leaders":         ", ".join(leaders),
        "node_labels":     node_labels,
        "node_colors":     node_colors,
        "node_customdata": node_customdata,
        "sources":         sources,
        "targets":         targets,
        "values":          values,
        "link_colors":     link_colors,
    }


def build_html():
    data_all = {yr: build_year_data(yr) for yr in YEARS}
    data_json = json.dumps(data_all, ensure_ascii=False)

    legend_lines = "".join(
        f'<span class="leg-item"><span class="leg-dot" style="background:{LINE_COLORS[ln]}"></span>{ln}</span>'
        for ln in ALL_LINES
    )
    legend_fares = "".join(
        f'<span class="leg-item"><span class="leg-dot" style="background:{FARE_COLORS[fn]}"></span>{fn}</span>'
        for fn in ALL_FARES
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sankey Metro Santiago 2010-2025</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #111113;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    padding: 18px 24px 28px;
  }}
  .header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 16px;
  }}
  .header-label {{
    font-size: 13px;
    color: #888;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    flex-shrink: 0;
  }}
  #yr-slider {{
    flex: 1;
    -webkit-appearance: none;
    height: 4px;
    border-radius: 2px;
    background: #333;
    outline: none;
    cursor: pointer;
  }}
  #yr-slider::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 18px; height: 18px;
    border-radius: 50%;
    background: #cccccc;
    cursor: pointer;
    border: 2px solid #555;
  }}
  #yr-slider::-moz-range-thumb {{
    width: 18px; height: 18px;
    border-radius: 50%;
    background: #cccccc;
    cursor: pointer;
    border: 2px solid #555;
  }}
  .year-badge {{
    font-size: 22px;
    font-weight: 700;
    color: #f0f0f0;
    min-width: 58px;
    text-align: center;
    flex-shrink: 0;
  }}
  .btn-anim {{
    background: #1e1e22;
    color: #ddd;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 6px 18px;
    font-size: 13px;
    cursor: pointer;
    flex-shrink: 0;
  }}
  .btn-anim:hover {{ background: #2a2a30; }}
  .stats-row {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 14px;
  }}
  .stat-card {{
    background: #1c1c1e;
    border: 1px solid #2a2a2e;
    border-radius: 8px;
    padding: 10px 14px;
  }}
  .stat-label {{
    font-size: 10px;
    color: #666;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .stat-val {{
    font-size: 22px;
    font-weight: 700;
    color: #f0f0f0;
    line-height: 1.15;
  }}
  .stat-val.small {{ font-size: 14px; }}
  #sankey-plot {{ width: 100%; }}
  .legend-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px 18px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #222;
  }}
  .leg-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #aaa;
  }}
  .leg-dot {{
    width: 10px; height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
  }}
  .footnote {{
    font-size: 11px;
    color: #555;
    margin-top: 10px;
    line-height: 1.5;
  }}
</style>
</head>
<body>

<div class="header">
  <span class="header-label">Año</span>
  <input type="range" id="yr-slider" min="2010" max="2025" value="2010" step="1">
  <span class="year-badge" id="yr-badge">2010</span>
  <button class="btn-anim" id="btn-play">&#9654; Animar</button>
</div>

<div class="stats-row">
  <div class="stat-card">
    <div class="stat-label">Total Pasajeros</div>
    <div class="stat-val" id="stat-total">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Líneas Activas</div>
    <div class="stat-val" id="stat-lines">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Líderes</div>
    <div class="stat-val small" id="stat-leaders">—</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Tipo Tarifa</div>
    <div class="stat-val small" id="stat-fares">Disponible</div>
  </div>
</div>

<div id="sankey-plot"></div>

<div class="legend-wrap">
  {legend_lines}
  <span style="border-left:1px solid #333;margin:0 6px;"></span>
  {legend_fares}
</div>

<div class="footnote">
  Fuente: Metro S.A. &mdash; Tabla A18 (afluencia por línea) y Tabla A19 (transacciones por tipo de tarifa).
  El grosor de cada flujo es proporcional a los pasajeros. Los tipos de pago sólo están disponibles desde 2010.
</div>

<script>
const DATA = {data_json};
const YEARS = {json.dumps(YEARS)};

const LAYOUT = {{
  paper_bgcolor: '#111113',
  plot_bgcolor:  '#111113',
  font: {{ family: "'Segoe UI', Arial, sans-serif", size: 12, color: '#cccccc' }},
  margin: {{ t: 36, b: 8, l: 10, r: 10 }},
  height: 490,
  annotations: [
    {{ x: 0.01, y: 1.07, xref: 'paper', yref: 'paper', text: '<b>AÑO</b>',
       showarrow: false, font: {{ size: 10, color: '#666' }}, xanchor: 'left' }},
    {{ x: 0.44, y: 1.07, xref: 'paper', yref: 'paper', text: '<b>LÍNEAS</b>',
       showarrow: false, font: {{ size: 10, color: '#666' }}, xanchor: 'center' }},
    {{ x: 0.93, y: 1.07, xref: 'paper', yref: 'paper', text: '<b>TIPO PAGO</b>',
       showarrow: false, font: {{ size: 10, color: '#666' }}, xanchor: 'center' }},
  ],
}};

function makeSankeyTrace(yr) {{
  const d = DATA[yr];
  return {{
    type: 'sankey',
    arrangement: 'snap',
    node: {{
      label:      d.node_labels,
      color:      d.node_colors,
      customdata: d.node_customdata,
      pad:        20,
      thickness:  18,
      line: {{ color: 'rgba(255,255,255,0.12)', width: 0.5 }},
      hovertemplate: '<b>%{{label}}</b><br>%{{customdata}}<extra></extra>',
    }},
    link: {{
      source: d.sources,
      target: d.targets,
      value:  d.values,
      color:  d.link_colors,
      hovertemplate: '%{{source.label}} → %{{target.label}}<br><b>%{{value:.1f}} M viajes</b><extra></extra>',
    }},
  }};
}}

// Render inicial
Plotly.newPlot('sankey-plot', [makeSankeyTrace(2010)], LAYOUT, {{
  displayModeBar: false,
  responsive: true,
}});

function updateStats(yr) {{
  const d = DATA[yr];
  document.getElementById('stat-total').textContent   = d.total.toFixed(1) + 'M';
  document.getElementById('stat-lines').textContent   = d.n_lines;
  document.getElementById('stat-leaders').textContent = d.leaders;
  document.getElementById('yr-badge').textContent     = yr;
  document.getElementById('yr-slider').value          = yr;
}}

updateStats(2010);

let currentYear = 2010;

function goToYear(yr) {{
  yr = parseInt(yr);
  if (yr === currentYear) return;
  currentYear = yr;
  updateStats(yr);
  Plotly.react('sankey-plot', [makeSankeyTrace(yr)], LAYOUT, {{
    displayModeBar: false, responsive: true,
  }});
}}

// ── Slider: solo cambia al soltar (mouseup / touchend) ────────────────────────
const slider = document.getElementById('yr-slider');
let isDragging = false;

slider.addEventListener('mousedown',  () => {{ isDragging = true; }});
slider.addEventListener('touchstart', () => {{ isDragging = true; }}, {{ passive: true }});

// Actualiza solo el badge mientras se arrastra
slider.addEventListener('input', () => {{
  document.getElementById('yr-badge').textContent = slider.value;
}});

window.addEventListener('mouseup', () => {{
  if (!isDragging) return;
  isDragging = false;
  goToYear(slider.value);
}});
window.addEventListener('touchend', () => {{
  if (!isDragging) return;
  isDragging = false;
  goToYear(slider.value);
}});

// ── Animación ─────────────────────────────────────────────────────────────────
let animTimer = null;

function stopAnim() {{
  clearInterval(animTimer);
  animTimer = null;
  document.getElementById('btn-play').innerHTML = '&#9654; Animar';
}}

function startAnim() {{
  document.getElementById('btn-play').innerHTML = '&#9646;&#9646; Pausar';
  animTimer = setInterval(() => {{
    let next = currentYear + 1;
    if (next > 2025) next = 2010;
    goToYear(next);
  }}, 1600);
}}

document.getElementById('btn-play').addEventListener('click', () => {{
  if (animTimer) stopAnim();
  else startAnim();
}});
</script>
</body>
</html>"""


if __name__ == "__main__":
    html = build_html()
    output_path = "sankey_metro_santiago.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Archivo guardado: {output_path}")