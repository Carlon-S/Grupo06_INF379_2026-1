# -*- coding: utf-8 -*-
"""
Treemap jerárquico de transacciones del sistema de transporte de Santiago por
modo (Metro / Buses / Metrotrén) y tipo de tarifa, año 2024.
Proyecto - Visualización de Datos (INF379), Grupo 06.
Autores: Diego Carlon y Joshua Serin (visualización conjunta).

Fuente de datos:
    Tabla A19 "Transacciones por tipo de tarifa" (Sistema RED, Metro y
    Metrotrén Nos), 2010-2025.
    Archivo: data/raw/Datos Transporte.xlsx,
             hoja "Metro Tr tipo de tarifa 2010-25".

Dependencia adicional:
    squarify  ->  pip install squarify
    (agregar a requirements.txt). Es una librería pequeña y pura de Python.

Uso:
    Ejecutar con el entorno que tiene instalado requirements.txt + squarify.
    Genera el PNG en esta misma carpeta.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import squarify

# --- Rutas robustas relativas a este archivo ----------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]                  # visualizaciones/ -> Proyecto/ -> repo
EXCEL_PATH = REPO_ROOT / "data" / "raw" / "Datos Transporte.xlsx"
OUTPUT_PATH = SCRIPT_DIR / "treemap_tarifas_grupal.py".replace(".py", ".png")

ANIO = 2024
HOJA = "Metro Tr tipo de tarifa 2010-25"

# Columnas (por posición) de la hoja: grupo -> {tarifa: índice de columna}
COLS_MODO = {
    "Metro":     {"Adulto": 15, "Estudiante media": 16,
                  "Estudiante básica": 17, "Adulto Mayor": 18},
    "Buses":     {"Adulto": 9,  "Estudiante media": 10,
                  "Estudiante básica": 11, "Adulto Mayor": 12},
    "Metrotrén": {"Adulto": 21, "Estudiante media": 22,
                  "Estudiante básica": 23, "Adulto Mayor": 24},
}

# Un tono base por modo; las tarifas se diferencian por luminancia.
COLOR_MODO = {"Metro": "#1f6f6f", "Buses": "#2b5d8c", "Metrotrén": "#9c5210"}
ORDEN_TARIFA = ["Adulto", "Estudiante media", "Estudiante básica", "Adulto Mayor"]


def cargar_datos(excel_path: Path, anio: int) -> dict:
    """Devuelve {modo: {tarifa: transacciones}} para el año pedido."""
    if not excel_path.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel en:\n  {excel_path}\n"
            "Verifica que ejecutas el script dentro del repositorio del grupo."
        )

    raw = pd.read_excel(excel_path, sheet_name=HOJA, header=None)
    fila = raw.index[raw[1] == anio]
    if len(fila) == 0:
        raise ValueError(f"No se encontró la fila anual del año {anio}.")
    r = fila[0]

    datos = {}
    for modo, tarifas in COLS_MODO.items():
        d = {}
        for tarifa, col in tarifas.items():
            v = pd.to_numeric(raw.iat[r, col], errors="coerce")  # '-' / NaN -> NaN
            if pd.notna(v) and v > 0:
                d[tarifa] = float(v)
        if d:
            datos[modo] = d
    return datos


def aclarar(color_hex: str, factor: float) -> tuple:
    """Aclara un color hacia blanco. factor=0 -> original, 1 -> blanco."""
    import matplotlib.colors as mcolors
    rgb = np.array(mcolors.to_rgb(color_hex))
    return tuple(rgb + (1.0 - rgb) * factor)


def graficar(datos: dict, anio: int, output_path: Path) -> None:
    total_sistema = sum(sum(t.values()) for t in datos.values())

    # Nivel 1: tamaño de cada modo
    modos = list(datos.keys())
    tam_modos = [sum(datos[m].values()) for m in modos]

    W, H = 100.0, 100.0
    norm_modos = squarify.normalize_sizes(tam_modos, W, H)
    rects_modos = squarify.squarify(norm_modos, 0, 0, W, H)

    fig, ax = plt.subplots(figsize=(12, 8))

    for modo, rect in zip(modos, rects_modos):
        x, y, dx, dy = rect["x"], rect["y"], rect["dx"], rect["dy"]

        # Nivel 2: tarifas dentro del rectángulo del modo
        tarifas = [t for t in ORDEN_TARIFA if t in datos[modo]]
        tam_tar = [datos[modo][t] for t in tarifas]
        norm_tar = squarify.normalize_sizes(tam_tar, dx, dy)
        rects_tar = squarify.squarify(norm_tar, x, y, dx, dy)

        for k, (tarifa, rt) in enumerate(zip(tarifas, rects_tar)):
            color = aclarar(COLOR_MODO[modo], 0.12 + 0.22 * k)
            ax.add_patch(Rectangle((rt["x"], rt["y"]), rt["dx"], rt["dy"],
                                   facecolor=color, edgecolor="white", linewidth=1.5))
            val = datos[modo][tarifa]
            pct = val / total_sistema * 100
            # Etiquetar solo si la celda es lo bastante ancha y alta (evita que
            # el texto se desborde en bloques delgados como Metrotrén).
            if rt["dx"] > 9 and rt["dy"] > 6:
                txt_color = "white" if k <= 1 else "#222222"
                ax.text(rt["x"] + rt["dx"] / 2, rt["y"] + rt["dy"] / 2,
                        f"{tarifa}\n{val/1e6:.0f} M  ({pct:.1f}%)",
                        ha="center", va="center", fontsize=8.5, color=txt_color,
                        clip_on=True)

        # Etiqueta del modo (borde grueso + título arriba del bloque)
        ax.add_patch(Rectangle((x, y), dx, dy, fill=False,
                               edgecolor=COLOR_MODO[modo], linewidth=3))
        pct_modo = sum(datos[modo].values()) / total_sistema * 100
        ax.text(x + 1.2, y + dy - 1.5, f"{modo.upper()}  ·  {pct_modo:.0f}%",
                ha="left", va="top", fontsize=11, fontweight="bold",
                color=COLOR_MODO[modo],
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.invert_yaxis()          # origen arriba-izquierda, lectura natural
    ax.axis("off")

    ax.set_title(f"Transacciones del transporte público de Santiago por modo y "
                 f"tipo de tarifa ({anio})",
                 fontsize=14, fontweight="bold", pad=16)
    fig.text(0.01, 0.01,
             "Fuente: Tabla A19 'Transacciones por tipo de tarifa' (Sistema RED, "
             "Metro y Metrotrén Nos), DTPM. El área es proporcional al número de "
             "transacciones.",
             fontsize=8, color="#444444")

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Imagen guardada en:\n  {output_path}")


def main() -> None:
    datos = cargar_datos(EXCEL_PATH, ANIO)
    print(f"Año {ANIO} — transacciones por modo (millones):")
    for modo, t in datos.items():
        print(f"  {modo}: {sum(t.values())/1e6:.0f} M  -> "
              + ", ".join(f"{k}={v/1e6:.0f}M" for k, v in t.items()))
    graficar(datos, ANIO, OUTPUT_PATH)


if __name__ == "__main__":
    main()
