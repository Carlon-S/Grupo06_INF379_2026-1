"""
Diagrama Sankey – Flujo de Pasajeros del Metro de Santiago (2010-2026)
Período ──► Línea ──► Tipo de Tarifa
Fuente: Metro de Santiago S.A. – Tablas A18 y Metro mensual 2010-2026
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import matplotlib.patheffects as pe
import warnings
warnings.filterwarnings('ignore')

# ── 1. Load data ──────────────────────────────────────────────────────────────
df1 = pd.read_excel('DatosTransporte.xlsx',
                    sheet_name='Metro 2010-24', header=3, index_col=0)
df2 = pd.read_excel('DatosTransporte.xlsx',
                    sheet_name='Metro 2025-26', header=3, index_col=0)

for df in [df1, df2]:
    df.dropna(subset=['Total Red'], inplace=True)
df1.index = pd.to_datetime(df1.index)
df2.index = pd.to_datetime(df2.index)
df = pd.concat([df1, df2])
df['year'] = df.index.year

lines_cols = {
    'Línea 1':  ('Total Linea 1',  'Pasajeros comunes.1', 'Escolares Pagados1.1', 'Escolares Básicos (Gratuitos).1'),
    'Línea 2':  ('Total Linea 2',  'Pasajeros comunes.2', 'Escolares Pagados1.2', 'Escolares Básicos (Gratuitos).2'),
    'Línea 3':  ('Total Linea 3',  'Pasajeros comunes.7', 'Escolares Pagados1.7', 'Escolares Básicos (Gratuitos).7'),
    'Línea 4':  ('Total Linea 4',  'Pasajeros comunes.3', 'Escolares Pagados1.3', 'Escolares Básicos (Gratuitos).3'),
    'Línea 4A': ('Total Linea 4A', 'Pasajeros comunes.4', 'Escolares Pagados1.4', 'Escolares Básicos (Gratuitos).4'),
    'Línea 5':  ('Total Linea 5',  'Pasajeros comunes.5', 'Escolares Pagados1.5', 'Escolares Básicos (Gratuitos).5'),
    'Línea 6':  ('Total Linea 6',  'Pasajeros comunes.6', 'Escolares Pagados1.6', 'Escolares Básicos (Gratuitos).6'),
}

def period_label(y):
    if y <= 2014:   return '2010–2014'
    elif y <= 2019: return '2015–2019'
    elif y <= 2022: return '2020–2022'
    else:           return '2023–2026'

df['period'] = df['year'].apply(period_label)
periods   = ['2010–2014', '2015–2019', '2020–2022', '2023–2026']
line_list = list(lines_cols.keys())
pay_keys  = ['Adultos', 'Escolares Pagados', 'Escolares Gratuitos']
pay_labels= ['Adultos', 'Escolares\nPagados', 'Escolares\nGratuitos']

# ── 2. Aggregate ──────────────────────────────────────────────────────────────
records = []
for period_name in periods:
    grp = df[df['period'] == period_name]
    for line, (tot_col, com_col, esc_p_col, esc_g_col) in lines_cols.items():
        if tot_col not in grp.columns:
            continue
        total = grp[tot_col].sum()
        if total == 0:
            continue
        comunes  = grp[com_col].sum()   if com_col   in grp.columns else 0
        esc_pag  = grp[esc_p_col].sum() if esc_p_col in grp.columns else 0
        esc_grat = grp[esc_g_col].sum() if esc_g_col in grp.columns else 0
        records.append({
            'period': period_name, 'line': line,
            'Adultos': comunes, 'Escolares Pagados': esc_pag,
            'Escolares Gratuitos': esc_grat
        })

agg = pd.DataFrame(records)

period_totals  = {p: agg[agg['period']==p][pay_keys].values.sum()/1e6 for p in periods}
line_totals    = {l: agg[agg['line']==l][pay_keys].values.sum()/1e6 for l in line_list}
payment_totals = {k: agg[k].sum()/1e6 for k in pay_keys}
grand_total    = sum(period_totals.values())

# ── 3. Colours ─────────────────────────────────────────────────────────────────
line_colors = {
    'Línea 1':  '#E8312A',
    'Línea 2':  '#F5A623',
    'Línea 3':  '#8B5E3C',
    'Línea 4':  '#1A3F9E',
    'Línea 4A': '#63B3E8',
    'Línea 5':  '#2CA836',
    'Línea 6':  '#9B30D4',
}
period_colors  = ['#1B4332', '#2D6A4F', '#52B788', '#95D5B2']
payment_colors = {
    'Adultos':            '#1D3D6E',
    'Escolares Pagados':  '#457B9D',
    'Escolares Gratuitos':'#7FBCD2',
}

# ── 4. Node layout ─────────────────────────────────────────────────────────────
GAP     = 0.018
NODE_W  = 0.048
X_LEFT  = 0.09
X_MID   = 0.50
X_RIGHT = 0.91

def node_positions(labels, values, total):
    usable = 1.0 - GAP * (len(labels) - 1)
    pos, y = [], 0.0
    for v in values:
        h = (v / total) * usable
        pos.append((y, y + h, y + h / 2))
        y += h + GAP
    return pos

period_pos  = node_positions(periods,   [period_totals[p]  for p in periods],  grand_total)
line_pos    = node_positions(line_list, [line_totals[l]    for l in line_list], grand_total)
payment_pos = node_positions(pay_keys,  [payment_totals[k] for k in pay_keys],  grand_total)

# ── 5. Bezier ribbon helper ────────────────────────────────────────────────────
def draw_ribbon(ax, x0, y0b, y0t, x1, y1b, y1t, color, alpha=0.42):
    cx = (x0 + x1) / 2
    verts = [(x0,y0b),(cx,y0b),(cx,y1b),(x1,y1b),
             (x1,y1t),(cx,y1t),(cx,y0t),(x0,y0t),(x0,y0b)]
    codes = [Path.MOVETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CLOSEPOLY]
    ax.add_patch(mpatches.PathPatch(
        Path(verts, codes), facecolor=color, edgecolor='none', alpha=alpha, zorder=1))

# ── 6. Build figure ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(22, 12))
ax.set_xlim(0, 1); ax.set_ylim(-0.06, 1.10); ax.axis('off')
fig.patch.set_facecolor('#F7F7F4')

usable = 1.0 - GAP * (max(len(periods), len(line_list), len(pay_keys)) - 1)

# ── Period → Line ribbons ──────────────────────────────────────────────────────
period_r_off = {p: period_pos[i][0] for i, p in enumerate(periods)}
line_l_off   = {l: line_pos[i][0]   for i, l in enumerate(line_list)}
line_r_off   = {l: line_pos[i][0]   for i, l in enumerate(line_list)}
pay_l_off    = {k: payment_pos[i][0] for i, k in enumerate(pay_keys)}

for _, row in agg.iterrows():
    p, l = row['period'], row['line']
    val = (row['Adultos'] + row['Escolares Pagados'] + row['Escolares Gratuitos']) / 1e6
    h   = (val / grand_total) * usable
    draw_ribbon(ax,
                X_LEFT + NODE_W, period_r_off[p], period_r_off[p] + h,
                X_MID  - NODE_W, line_l_off[l],   line_l_off[l]   + h,
                color=line_colors[l], alpha=0.38)
    period_r_off[p] += h
    line_l_off[l]   += h

# ── Line → Payment ribbons ─────────────────────────────────────────────────────
line_pay_agg = agg.groupby('line')[pay_keys].sum()
for line in line_list:
    if line not in line_pay_agg.index: continue
    for pk in pay_keys:
        val = line_pay_agg.loc[line, pk] / 1e6
        if val <= 0: continue
        h = (val / grand_total) * usable
        draw_ribbon(ax,
                    X_MID   + NODE_W, line_r_off[line],  line_r_off[line]  + h,
                    X_RIGHT - NODE_W, pay_l_off[pk],     pay_l_off[pk]     + h,
                    color=payment_colors[pk], alpha=0.48)
        line_r_off[line] += h
        pay_l_off[pk]    += h

# ── Draw period nodes ──────────────────────────────────────────────────────────
for i, (p, color) in enumerate(zip(periods, period_colors)):
    y0, y1, ym = period_pos[i]
    ax.add_patch(mpatches.FancyBboxPatch(
        (X_LEFT-NODE_W, y0), 2*NODE_W, y1-y0,
        boxstyle='round,pad=0.004', facecolor=color,
        edgecolor='white', linewidth=1.8, zorder=3))
    ax.text(X_LEFT, ym, f'{p}\n{period_totals[p]:.0f} M',
            ha='center', va='center', fontsize=9.5, fontweight='bold',
            color='white', zorder=5,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='black')])

# ── Draw line nodes ────────────────────────────────────────────────────────────
for i, line in enumerate(line_list):
    if line_totals[line] == 0: continue
    y0, y1, ym = line_pos[i]
    ax.add_patch(mpatches.FancyBboxPatch(
        (X_MID-NODE_W, y0), 2*NODE_W, y1-y0,
        boxstyle='round,pad=0.004', facecolor=line_colors[line],
        edgecolor='white', linewidth=1.8, zorder=3))
    ax.text(X_MID, ym, f'{line}\n{line_totals[line]:.0f} M',
            ha='center', va='center', fontsize=9.0, fontweight='bold',
            color='white', zorder=5,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='black')])

# ── Draw payment nodes ─────────────────────────────────────────────────────────
for i, (pk, pl, color) in enumerate(zip(pay_keys, pay_labels,
                                         list(payment_colors.values()))):
    y0, y1, ym = payment_pos[i]
    ax.add_patch(mpatches.FancyBboxPatch(
        (X_RIGHT-NODE_W, y0), 2*NODE_W, y1-y0,
        boxstyle='round,pad=0.004', facecolor=color,
        edgecolor='white', linewidth=1.8, zorder=3))
    ax.text(X_RIGHT, ym, f'{pl}\n{payment_totals[pk]:.0f} M',
            ha='center', va='center', fontsize=9.0, fontweight='bold',
            color='white', zorder=5,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='black')])

# ── Column headers ─────────────────────────────────────────────────────────────
for x, lbl in [(X_LEFT,'PERÍODO'), (X_MID,'LÍNEA'), (X_RIGHT,'TIPO DE TARIFA')]:
    ax.text(x, 1.055, lbl, ha='center', va='center',
            fontsize=13, fontweight='bold', color='#1a1a2e',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#E2E2DF',
                      edgecolor='#AAAAAA', alpha=0.95))

# ── Arrow guides ───────────────────────────────────────────────────────────────
for x0, x1 in [(X_LEFT+NODE_W+0.01, X_MID-NODE_W-0.01),
               (X_MID +NODE_W+0.01, X_RIGHT-NODE_W-0.01)]:
    ax.annotate('', xy=(x1, 1.055), xytext=(x0, 1.055),
                arrowprops=dict(arrowstyle='->', color='#AAAAAA', lw=1.5))

# ── Title & source ─────────────────────────────────────────────────────────────
ax.text(0.5, 1.095,
        'Flujo de Pasajeros del Metro de Santiago (2010–2026)',
        ha='center', va='center', fontsize=19, fontweight='bold',
        color='#1a1a2e', transform=ax.transAxes,
        fontfamily='DejaVu Sans')

ax.text(0.5, -0.05,
        'Fuente: Metro de Santiago S.A. – Tablas A18 y Metro mensual 2010-2026  '
        '|  Valores en millones de pasajeros transportados',
        ha='center', va='center', fontsize=9, color='#666',
        style='italic', transform=ax.transAxes)

plt.tight_layout(rect=[0, 0.03, 1, 0.98])
plt.savefig('Sankey_Metro_Santiago.png',
            dpi=200, bbox_inches='tight', facecolor='#F7F7F4')
print('Saved.')