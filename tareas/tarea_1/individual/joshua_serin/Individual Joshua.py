import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ruta = "DatosTransporte.xlsx"

# ── 1. Función para leer cada hoja ──────────────────────────────────────────
def leer_hoja(sheet_name):
    df = pd.read_excel(
        ruta,
        sheet_name=sheet_name,
        header=3,
        skiprows=0
    )
    
    # Eliminar columnas completamente vacías
    df = df.dropna(axis=1, how="all")
    
    # Ahora sí renombrar la primera columna como fecha
    df = df.rename(columns={df.columns[0]: "fecha"})
    
    # Parsear fecha
    for fmt in ["%b-%y", "%b-%Y", "%m-%Y", "%Y-%m"]:
        fechas = pd.to_datetime(df["fecha"], format=fmt, errors="coerce")
        if fechas.notna().sum() > 5:
            df["fecha"] = fechas
            break

    df = df.dropna(subset=["fecha"])
    return df

# ── 2. Leer y unir ambas hojas ───────────────────────────────────────────────
df_hist  = leer_hoja("Metro 2010-24")
df_recnt = leer_hoja("Metro 2025-26")

df = pd.concat([df_hist, df_recnt], ignore_index=True)
df = df.sort_values("fecha").reset_index(drop=True)


# ── 3. Renombrar columnas clave ──────────────────────────────────────────────
df = df.rename(columns={
    "Total Red":     "Total Red",
    "Total Linea 1": "Linea 1",
    "Total Linea 2": "Linea 2",
    "Total Linea 3": "Linea 3",
    "Total Linea 4": "Linea 4",
    "Total Linea 4A": "Linea 4A",
    "Total Linea 5": "Linea 5",
    "Total Linea 6": "Linea 6",
})

# ── 4. Limpiar columnas numéricas ────────────────────────────────────────────
lineas = ["Linea 1", "Linea 2", "Linea 3", "Linea 4","Linea 4A", "Linea 5", "Linea 6"]

for col in lineas:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ── 5. Colores Metro Santiago ────────────────────────────────────────────────
colores = {
    "Linea 1": "#EF3E42",
    "Linea 2": "#F3C910",
    "Linea 3": "#754A12",
    "Linea 4": "#180DBB",
    "Linea 4A": "#278AE7",
    "Linea 5": "#22C430",
    "Linea 6": "#A517E7",
}

# ── 6. Stream graph ──────────────────────────────────────────────────────────
fig = go.Figure()

for linea in lineas:
    fig.add_trace(go.Scatter(
        x=df["fecha"],
        y=df[linea],
        name=linea,
        mode="lines",
        line=dict(width=0.5, color=colores.get(linea, "#999")),
        fillcolor=colores.get(linea, "#999"),
        stackgroup="metro",
        groupnorm="",
    ))

# ── 7. Layout ────────────────────────────────────────────────────────────────
fig.update_layout(
    # Título centrado y en negrita
    title=dict(
        text="<b>Uso del Metro de Santiago por Línea (2010–2026)</b>",
        x=0.5,
        xanchor="center",
        font=dict(size=22, family="Arial Black", color="#1a1a1a")
    ),


    xaxis=dict(
        title=dict(text="<b>Fecha</b>", font=dict(size=14, family="Arial Black")),
        showgrid=False,
        showline=True,
        linecolor="#cccccc",
        tickfont=dict(size=12, family="Arial", color="#444444"),
    ),
    yaxis=dict(
        title=dict(text="<b>Pasajeros transportados</b>", font=dict(size=14, family="Arial Black")),
        showgrid=True,
        gridcolor="#eeeeee",
        tickformat=",",
        tickfont=dict(size=12, family="Arial", color="#444444"),
    ),


    legend=dict(
        title=dict(text="<b>Línea</b>", font=dict(size=13, family="Arial Black")),
        orientation="h",
        x=0.5,
        xanchor="center",
        y=-0.18,
        font=dict(size=12, family="Arial"),
        bgcolor="rgba(0,0,0,0)",
    ),

    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=80, b=100, l=80, r=40),
)

fig.show()