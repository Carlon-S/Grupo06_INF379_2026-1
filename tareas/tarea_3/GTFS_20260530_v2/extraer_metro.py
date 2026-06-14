import pandas as pd
import re

# -----------------------------
# Cargar archivos GTFS
# -----------------------------

stops = pd.read_csv("stops.txt")
trips = pd.read_csv("trips.txt")
stop_times = pd.read_csv("stop_times.txt")

# -----------------------------
# Filtrar solo líneas Metro
# -----------------------------

lineas_metro = ["L1", "L2", "L3", "L4", "L4A", "L5", "L6"]

trips_metro = trips[trips["route_id"].isin(lineas_metro)]

# -----------------------------
# Relacionar trips con estaciones
# -----------------------------

metro_stop_times = stop_times.merge(
    trips_metro[["trip_id", "route_id"]],
    on="trip_id",
    how="inner"
)

# -----------------------------
# Relacionar con stops
# -----------------------------

metro_stops = metro_stop_times.merge(
    stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]],
    on="stop_id",
    how="left"
)

# -----------------------------
# Limpiar nombres
# -----------------------------

def limpiar_nombre(nombre):

    nombre = re.sub(
        r"\s+Dirección.*",
        "",
        str(nombre),
        flags=re.IGNORECASE
    )

    nombre = nombre.strip()

    return nombre

metro_stops["Estacion"] = metro_stops["stop_name"].apply(
    limpiar_nombre
)

# -----------------------------
# Agrupar líneas por estación
# -----------------------------

resultado = (
    metro_stops
    .groupby("Estacion")
    .agg({
        "route_id": lambda x: sorted(set(x)),
        "stop_lat": "mean",
        "stop_lon": "mean"
    })
    .reset_index()
)

# -----------------------------
# Crear columnas finales
# -----------------------------

resultado["Lineas"] = resultado["route_id"].apply(
    lambda x: ", ".join(x)
)

resultado["Combinacion"] = resultado["route_id"].apply(
    lambda x: "Sí" if len(x) > 1 else "No"
)

resultado.rename(
    columns={
        "stop_lat": "Latitud",
        "stop_lon": "Longitud"
    },
    inplace=True
)

resultado = resultado[
    [
        "Estacion",
        "Lineas",
        "Latitud",
        "Longitud",
        "Combinacion"
    ]
]

# -----------------------------
# Ordenar
# -----------------------------

resultado = resultado.sort_values(
    by="Estacion"
)

# -----------------------------
# Exportar CSV
# -----------------------------

resultado.to_csv(
    "metro_estaciones.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Archivo generado:")
print("metro_estaciones.csv")
print(f"Estaciones encontradas: {len(resultado)}")