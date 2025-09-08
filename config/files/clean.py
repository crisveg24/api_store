import pandas as pd
import os

def clean_csv(input_file, output_file):
    """
    Limpia el archivo CSV, maneja valores nulos y guarda un archivo limpio.
    
    :param input_file: Ruta del archivo CSV de entrada.
    :param output_file: Ruta del archivo CSV de salida.
    """
    try:
        # Leer el archivo CSV original
        df = pd.read_csv(input_file)

        # Mostrar los primeros registros para ver cómo está el archivo
        print("Primeros registros del CSV original:")
        print(df.head())

        # Limpiar los datos: Renombramos las columnas para asegurar consistencia
        df.columns = df.columns.str.strip()  # Eliminar espacios adicionales en los nombres de las columnas
        df.columns = df.columns.str.replace(' ', '_')  # Reemplazar espacios por guiones bajos

        # Verificar si las columnas tienen los nombres correctos
        print(f"Columnas después de limpieza: {df.columns.tolist()}")

        # Limpiar datos: Aquí puedes añadir las reglas de limpieza necesarias
        # Ejemplo de manejo de valores nulos:
        df = df.dropna()  # Elimina filas con valores nulos
        # También puedes rellenar valores nulos con algún valor por defecto:
        # df.fillna({'store_area': 0, 'items_available': 0}, inplace=True)

        # Asegurarse de que los tipos de datos sean correctos
        df['Store_Area'] = df['Store_Area'].astype(float)
        df['Items_Available'] = df['Items_Available'].astype(int)
        df['Daily_Customer_Count'] = df['Daily_Customer_Count'].astype(int)
        df['Store_Sales'] = df['Store_Sales'].astype(float)

        # Verificar si los datos están en el formato adecuado
        print("Primeros registros del CSV limpio:")
        print(df.head())

        # Guardar el archivo limpio en la ruta especificada
        df.to_csv(output_file, index=False)
        print(f"Archivo limpio guardado en: {output_file}")

    except Exception as e:
        print(f"Error al procesar el CSV: {e}")

# Definir las rutas del archivo CSV original y el archivo limpio
input_file = '/workspaces/api_store/config/files/Stores.csv'  
output_file = '/workspaces/api_store/config/files/Stores_clean.csv'  

# Llamar a la función para limpiar el CSV
clean_csv(input_file, output_file)
