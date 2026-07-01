# -*- coding: utf-8 -*-
"""
Ridgeline / Joyplot de afluencia mensual del Metro de Santiago (Total Red),
un perfil por año, 2010-2024.
Proyecto - Visualización de Datos (INF379), Grupo 06.
Autor: Joshua Serin.

Fuente de datos:
    "Número de pasajeros transportados (Total Red) por mes", Metro de Santiago.
    Archivo: data/raw/Datos Transporte.xlsx, hoja "Metro 2010-24".

Nota técnica:
    Aunque joypy figura en requirements.txt, esta versión está construida con
    matplotlib puro para evitar incompatibilidades de versión de joypy con
    matplotlib reciente. El tipo de gráfico es el mismo: un ridgeline (joyplot).

Uso:
    Ejecutar con el entorno que tiene instalado requirements.txt
    (pandas, numpy, matplotlib, openpyxl). Genera el PNG en esta misma carpeta.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize

# --- Rutas robustas relativas a este archivo ----------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]                  # visualizaciones/ -> Proyecto/ -> repo
EXCEL_PATH = REPO_ROOT / "data" / "raw" / "Datos Transporte.xlsx"
OUTPUT_PATH = SCRIPT_DIR / "ridgeline_afluencia_joshua.png"

MESES_CORTOS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def cargar_datos(excel_path: Path) -> pd.DataFrame:
    """Devuelve una matriz año x mes (12 columnas) con afluencia en millones."""
    if not excel_path.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel en:\n  {excel_path}\n"
            "Verifica que ejecutas el script dentro del repositorio del grupo."
        )

    df = pd.read_excel(excel_path, sheet_name="Metro 2010-24", header=3)
    df = df.dropna(axis=1, how="all")

    col_fecha = df.columns[0]          # 'Mes y año'
    col_total = "Total Red"

    df = df[df[col_fecha].notna()].copy()
    df["fecha"] = pd.to_datetime(df[col_fecha], errors="coerce")
    df = df[df["fecha"].notna()]
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    # Matriz año x mes en millones de pasajeros
    matriz = (df.pivot_table(index="anio", columns="mes",
                             values=col_total, aggfunc="sum") / 1e6)
    return matriz.sort_index()


def graficar(matriz: pd.DataFrame, output_path: Path) -> None:
    anios = matriz.index.tolist()
    n = len(anios)
    x = np.arange(12)

    vmin, vmax = np.nanmin(matriz.values), np.nanmax(matriz.values)
    escala = 1.9          # cuánto se "estira" cada cresta (controla el solape)
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap("viridis")

    fig, ax = plt.subplots(figsize=(11, 9))

    # 2010 arriba, 2024 abajo. Se dibuja de arriba hacia abajo para que los
    # años recientes (adelante) queden por encima (occlusión correcta).
    for i, anio in enumerate(anios):
        pos = (n - 1 - i)                  # línea base de la cresta
        vals = matriz.loc[anio].values.astype(float)
        altura = (vals - vmin) / (vmax - vmin) * escala
        color = cmap(0.1 + 0.8 * i / (n - 1))

        ax.fill_between(x, pos, pos + altura, color=color, alpha=0.85,
                        zorder=i, linewidth=0)
        ax.plot(x, pos + altura, color="white", linewidth=1.0, zorder=i)
        ax.text(-0.6, pos + 0.05, str(anio), ha="right", va="bottom",
                fontsize=9, fontweight="bold")

    # Anotaciones periodísticas sobre los dos hitos del periodo
    pos_2019 = n - 1 - anios.index(2019)
    pos_2020 = n - 1 - anios.index(2020)
    ax.annotate("Estallido social\n(oct–nov 2019)",
                xy=(9.3, pos_2019 + 0.15), xytext=(6.2, pos_2019 + 1.5),
                fontsize=8, color="#b30000", ha="center",
                arrowprops=dict(arrowstyle="->", color="#b30000", lw=1.2),
                zorder=n + 1)
    ax.annotate("Pandemia COVID-19\n(abr–jul 2020)",
                xy=(4.5, pos_2020 + 0.05), xytext=(2.0, pos_2020 + 1.6),
                fontsize=8, color="#b30000", ha="center",
                arrowprops=dict(arrowstyle="->", color="#b30000", lw=1.2),
                zorder=n + 1)

    # Ejes y estética
    ax.set_xticks(x)
    ax.set_xticklabels(MESES_CORTOS)
    ax.set_yticks([])
    ax.set_xlim(-1.5, 11.5)
    ax.set_ylim(-0.5, n + escala)
    for spine in ["left", "right", "top"]:
        ax.spines[spine].set_visible(False)
    ax.set_xlabel("Mes")

    # Barra de color (referencia de volumen)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("Afluencia mensual (millones de pasajeros)")

    ax.set_title("Afluencia mensual del Metro de Santiago por año, 2010–2024",
                 fontsize=14, fontweight="bold", pad=14)
    fig.text(0.01, 0.005,
             "Fuente: Metro de Santiago — 'Número de pasajeros transportados "
             "(Total Red)', hoja 'Metro 2010-24'.",
             fontsize=7.5, color="#444444")

    fig.tight_layout(rect=[0, 0.02, 1, 1])
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Imagen guardada en:\n  {output_path}")


def main() -> None:
    matriz = cargar_datos(EXCEL_PATH)
    print("Años cargados:", matriz.index.tolist())
    print(f"Rango de afluencia: {np.nanmin(matriz.values):.1f} – "
          f"{np.nanmax(matriz.values):.1f} millones/mes")
    graficar(matriz, OUTPUT_PATH)


if __name__ == "__main__":
    main()
