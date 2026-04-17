import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from matplotlib.lines import Line2D

# 1. CARGA Y LIMPIEZA DE DATOS
FILE = "Datos Transporte.xlsx"
df_raw = pd.read_excel(FILE, sheet_name="Afluencia de pasajeros 1990-25", header=None, engine="openpyxl")
df_raw.columns = df_raw.iloc[4]
df = df_raw.iloc[5:].copy()
df = df.rename(columns={df.columns[0]: "drop", df.columns[1]: "Año"}).drop(columns=["drop"])

line_cols = ["Línea1", "Línea 2", "Línea 3", "Línea 4", "Línea 4A", "Línea 5", "Línea 6"]

df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
df = df.dropna(subset=["Año"]).copy()
df["Año"] = df["Año"].astype(int)

for col in line_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df[(df["Año"] >= 1990) & (df["Año"] <= 2025)].copy().reset_index(drop=True)

# 2. CÁLCULO DE RANKINGS Y PROPORCIONES
ranking_data = []
for _, row in df.iterrows():
    año = row["Año"]
    vals = {col: row[col] for col in line_cols if pd.notna(row[col]) and row[col] != 0}
    total = sum(vals.values())

    if len(vals) >= 1:
        sorted_lines = sorted(vals, key=vals.get, reverse=True)
        for rank, line in enumerate(sorted_lines, 1):
            ranking_data.append({
                "Año": año,
                "Línea": line,
                "Ranking": rank,
                "Proporcion": vals[line] / total if total > 0 else 0
            })

df_rank = pd.DataFrame(ranking_data)

años = sorted(df_rank["Año"].unique())
n_cols = len(años)
max_rank = int(df_rank["Ranking"].max())
x_pos = {año: i for i, año in enumerate(años)}

# 3. COLORES
LINE_COLORS = {
    "Línea1": "#CC0000",
    "Línea 2": "#DAA520",
    "Línea 3": "#8B4513",
    "Línea 4": "#1A237E",
    "Línea 4A": "#1565C0",
    "Línea 5": "#2E7D32",
    "Línea 6": "#6A0DAD",
}
LINE_LABELS = {k: k.replace("Línea1", "Línea 1") for k in LINE_COLORS}

MIN_H = 0.01
MAX_H = 0.40
GLOBAL_ALPHA = 0.65

def band_h(prop):
    return MIN_H + (MAX_H - MIN_H) * prop

def ribbon_path(x0, y0, h0, x1, y1, h1):
    mx = (x0 + x1) / 2
    verts = [
        (x0, y0-h0), (mx, y0-h0), (mx, y1-h1), (x1, y1-h1),
        (x1, y1+h1), (mx, y1+h1), (mx, y0+h0), (x0, y0+h0),
        (x0, y0-h0)
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.LINETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CLOSEPOLY
    ]
    return Path(verts, codes)

# 4. FIGURA
fig, ax = plt.subplots(figsize=(24, 11))
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

# --- FONDO SIN GRID  ---
for xi in range(n_cols):
    for rank in range(1, max_rank + 1):
        color_bg = "#F8F8F8" if rank % 2 == 0 else "#FFFFFF"
        ax.add_patch(
            patches.Rectangle(
                (xi - 0.5, rank - 0.5),
                1.0, 1.0,
                facecolor=color_bg,
                edgecolor="none",
                zorder=0
            )
        )

# --- RIBBONS ---
for linea in line_cols:
    color = LINE_COLORS[linea]
    sub = df_rank[df_rank["Línea"] == linea].sort_values("Año").set_index("Año")
    años_linea = sub.index.tolist()
    
    patches_list = []
    for i in range(len(años_linea) - 1):
        a0, a1 = años_linea[i], años_linea[i+1]
        if a1 - a0 != 1: continue

        r0, r1 = sub.loc[a0, "Ranking"], sub.loc[a1, "Ranking"]
        p0, p1 = sub.loc[a0, "Proporcion"], sub.loc[a1, "Proporcion"]
        x0, x1 = x_pos[a0], x_pos[a1]

        patches_list.append(patches.PathPatch(ribbon_path(x0, r0, band_h(p0), x1, r1, band_h(p1))))

        # Etiquetas de porcentaje (ZORDER 10)
        label_points = [(1992, 1993), (2003, 2004), (2007, 2008), (2011, 2012), (2022, 2023)]
        if (a0, a1) in label_points:
            p_avg = (p0 + p1) / 2
            ax.text((x0+x1)/2, (r0+r1)/2, f"{p_avg:.1%}", ha="center", va="center",
                    fontsize=8, fontweight="bold", color="#111111", zorder=10)

    # Nombre al final
    if años_linea:
        ultimo_año = años_linea[-1]
        ultimo_rank = sub.loc[ultimo_año, "Ranking"]
        ax.text(x_pos[ultimo_año] + 0.55, ultimo_rank, LINE_LABELS[linea],
                ha="left", va="center", fontsize=9, fontweight="bold", color=color, zorder=10)

    col = PatchCollection(patches_list, facecolor=color, edgecolor= None, 
                          alpha=GLOBAL_ALPHA, zorder=5, antialiased=True)
    ax.add_collection(col)

# 5. EJES
ax.set_xlim(-0.5, n_cols + 1.5)
ax.set_ylim(max_rank + 0.5, 0.5)
ax.set_xticks(list(x_pos.values()))
ax.set_xticklabels(años, fontsize=8, rotation=90, color="#444444")
ax.set_yticks(range(1, max_rank + 1))
ax.set_yticklabels([f"{i}º" for i in range(1, max_rank + 1)], fontsize=10, fontweight="bold")

ax.grid(False)
ax.tick_params(axis='y', length=0)
ax.set_xlabel("Año", fontsize=12, fontweight="bold")
ax.set_ylabel("Posición en el Ranking", fontsize=12, fontweight="bold")

for spine in ax.spines.values():
    spine.set_visible(False)

# 6. LEYENDA
legend_handles = [
    Line2D([0], [0], color=LINE_COLORS[k], lw=4, label=LINE_LABELS[k])
    for k in reversed(line_cols)
]
leg = ax.legend(handles=legend_handles, loc="lower left", bbox_to_anchor=(0.01, 0.05),
                fontsize=9, frameon=True, title="Líneas")
plt.setp(leg.get_title(), fontweight="bold")

# 7. TÍTULO Y NOTAS
ax.set_title("Evolución del Ranking y Cuota de Viajes - Metro de Santiago (1990–2025)",
             fontsize=16, fontweight="bold", pad=30)

fig.text(0.015, 0.015,
         "Grosor de banda representa % de participación anual sobre el total de la red.",
         fontsize=9, color="#666666", style="italic")

fig.text(0.015, 0.035,
         "Valores porcentuales indican participación promedio en puntos seleccionados.",
         fontsize=8, color="#666666", style="italic")

fig.text(0.985, 0.015,
         "Inauguraciones: L5 (1997), L4 (2005), L4A (2006), L6 (2017), L3 (2019)\n"
         "Fuente: Tabla A18 - Afluencia de pasajeros en millones de viajes por año (Metro S.A.)",
         fontsize=9, color="#666666", style="italic", ha="right")

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig("Ranked_Ribbon_Plot.png", dpi=200, bbox_inches="tight")
plt.close()

print("Imagen generada: Ranked_Ribbon_Plot.png")