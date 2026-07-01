# -*- coding: utf-8 -*-
"""
Heatmap de evasión en Buses RED (Transantiago) por mes y año, 2007-2025.
Proyecto - Visualización de Datos (INF379), Grupo 06.
Autor: Diego Carlon.

Fuente de datos:
    Tabla A24 "Evasión en buses, 2007-2025".
    Programa Nacional de Fiscalización (Ministerio de Transportes y
    Telecomunicaciones) y Directorio de Transporte Público Metropolitano (DTPM).
    Archivo: data/raw/Datos Transporte.xlsx, hoja "Evasión".

Uso:
    Ejecutar con el entorno que tiene instalado requirements.txt
    (pandas, numpy, matplotlib, openpyxl). Genera el PNG en esta misma carpeta.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# --- Rutas robustas: relativas a la ubicación de este archivo -----------------
# Estructura esperada:
#   Grupo06_INF379_2026-1/
#       data/raw/Datos Transporte.xlsx
#       Proyecto/visualizaciones/heatmap_evasion_diego.py   <-- este archivo
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]                      # visualizaciones/ -> Proyecto/ -> repo
EXCEL_PATH = REPO_ROOT / "data" / "raw" / "Datos Transporte.xlsx"
OUTPUT_PATH = SCRIPT_DIR / "heatmap_evasion_diego.png"

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
MESES_CORTOS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def cargar_datos(excel_path: Path) -> pd.DataFrame:
    """Carga y limpia la hoja 'Evasión'. Devuelve matriz años x meses en %."""
    if not excel_path.exists():
        raise FileNotFoundError(
            f"No se encontró el Excel en:\n  {excel_path}\n"
            "Verifica que ejecutas el script dentro del repositorio del grupo."
        )

    df = pd.read_excel(excel_path, sheet_name="Evasión", header=4)

    # 1) Quitar asteriscos del año (2013*, 2022**) y descartar filas de notas al
    #    pie: todo lo que no sea un año numérico se vuelve NaN y se elimina.
    df["Año"] = pd.to_numeric(
        df["Año"].astype(str).str.replace("*", "", regex=False),
        errors="coerce",
    )
    df = df.dropna(subset=["Año"]).copy()
    df["Año"] = df["Año"].astype(int)

    # 2) Texto 'sin medición' y celdas vacías -> NaN; valores a porcentaje (x100).
    matriz = (
        df.set_index("Año")[MESES]
        .replace("sin medición", np.nan)
        .apply(pd.to_numeric, errors="coerce")
        * 100.0
    )
    return matriz


def graficar(matriz: pd.DataFrame, output_path: Path) -> None:
    """Construye y guarda el heatmap."""
    data = np.ma.masked_invalid(matriz.values)  # celdas faltantes -> enmascaradas
    anios = matriz.index.tolist()

    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad("#e8e8e8")  # gris claro para meses sin dato
    norm = Normalize(vmin=np.nanmin(matriz.values), vmax=np.nanmax(matriz.values))

    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(data, aspect="auto", cmap=cmap, norm=norm)

    # Ejes
    ax.set_xticks(range(12))
    ax.set_xticklabels(MESES_CORTOS, rotation=45, ha="right")
    ax.set_yticks(range(len(anios)))
    ax.set_yticklabels(anios)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Año")

    # Líneas de separación entre celdas para mejorar la lectura
    ax.set_xticks(np.arange(-0.5, 12, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(anios), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", length=0)

    # Anotar cada celda con el valor (% entero) para que sea autoexplicativo.
    umbral = norm.vmin + 0.6 * (norm.vmax - norm.vmin)
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            v = matriz.values[i, j]
            if np.isnan(v):
                continue
            color = "white" if v >= umbral else "black"
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    fontsize=7, color=color)

    # Barra de color
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Tasa de evasión (%)")

    # Títulos y fuente
    ax.set_title("Evasión en Buses RED (Transantiago) por mes y año, 2007–2025",
                 fontsize=14, fontweight="bold", pad=14)
    fig.text(0.01, 0.005,
             "Fuente: Programa Nacional de Fiscalización (MTT) y DTPM — "
             "Tabla A24 'Evasión en buses'. (*) 2013–2021 medición trimestral/"
             "semestral; desde 2022 nueva metodología DTPM.",
             fontsize=7.5, color="#444444")

    fig.tight_layout(rect=[0, 0.02, 1, 1])
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Imagen guardada en:\n  {output_path}")


def main() -> None:
    matriz = cargar_datos(EXCEL_PATH)
    print("Años cargados:", matriz.index.tolist())
    print("Rango de evasión: "
          f"{np.nanmin(matriz.values):.1f}% - {np.nanmax(matriz.values):.1f}%")
    graficar(matriz, OUTPUT_PATH)


if __name__ == "__main__":
    main()
