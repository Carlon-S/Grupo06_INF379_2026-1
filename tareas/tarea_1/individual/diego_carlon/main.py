import pandas as pd
import matplotlib.pyplot as plt
import joypy
from matplotlib import cm

# 1. CARGA DE DATOS
# Ajusta el nombre exacto de tu archivo Excel
PATH_EXCEL = "../../../data/raw/Datos_Transporte.xlsx" 

# Cargar hoja de Pasajeros y hoja de Tarifas
df_pasajeros = pd.read_excel(PATH_EXCEL, sheet_name='Metro Tr tipo de tarifa 2010-25')
df_tarifas = pd.read_excel(PATH_EXCEL, sheet_name='Tarifas')

# 2. LIMPIEZA Y PREPARACIÓN (Criterio A y B)
# Filtramos solo las columnas que necesitas: Año, Mes y el Subtotal de Metro
# Nota: Asegúrate de que los nombres de columnas coincidan con tu Excel
df_clean = df_pasajeros[['Año', 'Mes', 'Subtotal Metro']].copy()

# Unimos con las tarifas para saber cuánto costaba el pasaje en cada fecha
# Tip: Necesitamos que 'Año' y 'Mes' existan en ambas hojas para el "merge"
df_final = pd.merge(df_clean, df_tarifas[['Año', 'Mes', 'Metro / Tren Hora Punta']], 
                     on=['Año', 'Mes'], how='left')

# 3. CREACIÓN DEL RIDGELINE (La "Cordillera")
plt.figure(figsize=(12, 8))

# Creamos el gráfico: 
# x_range: los meses o días, labels: los años
# color: usaremos el precio de la tarifa para el degradado (Criterio A)
fig, axes = joypy.joyplot(df_final, 
                          by="Año", 
                          column="Subtotal Metro", 
                          colormap=cm.viridis, # Colores según volumen/densidad
                          title="Evolución de Pasajeros Metro vs Tarifas (2010-2025)",
                          fade=True)

# 4. GUARDAR RESULTADO
plt.savefig("visualizacion_ridgeline_diego.png")
print("Gráfico generado con éxito en la carpeta individual.")