import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use('Agg')

# ── Datos: horario (filas) × motivo (columnas) ─────────────────────────────
# Obtenidos desde encuesta propia Google Forms, mayo 2026. N=35
# Pregunta multi-select: un encuestado puede aparecer en más de un horario/motivo

horarios = ['Punta\nMañana', 'F.P.\nMañana', 'Mediodía', 'F.P.\nTarde', 'Punta\nTarde', 'Noche']
motivos  = ['Estudio', 'Trabajo', 'Trámites', 'Ocio', 'Compras', 'Otro']

# Matriz de conteos: filas=horario, columnas=motivo
data = np.array([
    [ 8,  9,  9,  4,  3,  3],  # Punta mañana    (7:00 – 9:00)
    [12,  6,  7,  8,  4,  3],  # F.P. mañana     (9:00 – 12:00)
    [ 6,  3,  5,  3,  2,  3],  # Mediodía        (12:00 – 14:00)
    [ 9,  3,  5,  6,  2,  1],  # F.P. tarde      (14:00 – 18:00)
    [11, 10,  9,  5,  4,  1],  # Punta tarde     (18:00 – 20:00)
    [ 4,  5,  2,  1,  0,  0],  # Noche           (después de 20:00)
])

# ── Colores por motivo ──────────────────────────────────────────────────────
colors = ['#0ea5e9', '#1a56db', '#7c3aed', '#ec4899', '#f97316', '#eab308']
# ── Configuración del gráfico polar ────────────────────────────────────────
N      = len(horarios)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
width  = 2 * np.pi / N - 0.06  # ancho de cada pétalo con pequeño gap

fig = plt.figure(figsize=(13, 13))
ax  = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N')   # Norte = 12 en punto (inicio)
ax.set_theta_direction(-1)         # Dirección horaria

# ── Dibujar pétalos apilados ────────────────────────────────────────────────
for i, (angle, horario) in enumerate(zip(angles, horarios)):
    bottom = 0
    for j, (motivo, color) in enumerate(zip(motivos, colors)):
        val = data[i, j]
        if val == 0:
            continue
        ax.bar(
            angle, val, width=width, bottom=bottom,
            color=color, alpha=0.82, edgecolor='white', linewidth=1.2
        )
        # Etiqueta de valor dentro del pétalo si es suficientemente grande
        if val >= 4:
            mid_r = bottom + val / 2
            ax.text(angle, mid_r, str(val),
                    ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='white')
        bottom += val

    # Etiqueta del horario + total al borde exterior del pétalo
    total = data[i].sum()
    ax.text(angle, bottom + 1.8, f"{horario}\n({total})",
            ha='center', va='center',
            fontsize=10, fontweight='bold', color='#222')

# ── Estética del eje polar ──────────────────────────────────────────────────
ax.set_yticklabels([])
ax.set_xticks([])
ax.spines['polar'].set_visible(False)
ax.set_facecolor('#FAFAFA')
fig.patch.set_facecolor('white')

# Grillas de referencia suaves
max_val = data.sum(axis=1).max()
for r in range(5, int(max_val) + 5, 5):
    ax.plot(np.linspace(0, 2 * np.pi, 200), [r] * 200,
            color='#ddd', linewidth=0.7, zorder=0)
    ax.text(np.pi / N, r, str(r), fontsize=7.5, color='#aaa', ha='center')

# ── Leyenda ─────────────────────────────────────────────────────────────────
legend_patches = [mpatches.Patch(color=c, label=m, alpha=0.85)
                  for c, m in zip(colors, motivos)]
ax.legend(handles=legend_patches, title='Motivo de uso',
          title_fontsize=10.5, fontsize=10,
          loc='upper right', bbox_to_anchor=(1.32, 1.12),
          framealpha=0.95, edgecolor='#ccc')

# ── Títulos y fuente ─────────────────────────────────────────────────────────
fig.suptitle(
    'Distribución de Motivos de Uso por Horario\n'
    'Transporte Público en Santiago — Encuesta 2026',
    fontsize=15, fontweight='bold', color='#1a1a2e', y=0.97
)
ax.set_title(
    'Cada pétalo representa un horario · '
    'Su longitud indica la cantidad de respuestas · '
    'Colores = motivo de viaje',
    fontsize=9, color='#666', pad=22
)
fig.text(
    0.5, 0.02,
    'Fuente: Encuesta propia, Google Forms, mayo 2026  |  N = 35  |  '
    'Pregunta de selección múltiple, un encuestado puede aparecer en más de un horario.',
    ha='center', fontsize=8.5, color='#888'
)

# ── Exportar ─────────────────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0.04, 1, 0.95])
plt.savefig('NightingaleRose_Grupal_Tarea2.png',
            dpi=180, bbox_inches='tight', facecolor='white')
plt.close()
print("Gráfico guardado como NightingaleRose_Grupal_Tarea2.png")