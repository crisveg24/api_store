import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models.store_model import Base, Store  
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno desde .env
load_dotenv()

# URI de conexión para SQLite
SQLITE_URI = 'sqlite:///stores.db'

def get_engine():
    """
    Intenta crear una conexión con SQLite.
    """
    try:
        engine = create_engine(SQLITE_URI, echo=True)
        # Probar conexión
        conn = engine.connect()
        conn.close()
        logging.info('Conexión a SQLite exitosa.')
        return engine
    except OperationalError as e:
        logging.error(f'No se pudo conectar a SQLite: {e}')
        raise

# Crear el motor de conexión
engine = get_engine()
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)  # Crear las tablas

def load_data_from_csv():
    """
    Carga los datos desde el archivo CSV a la base de datos.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'config', 'Stores.csv')  
    logging.info(f"Archivo CSV localizado en: {file_path}")

    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        logging.info(f"Datos del CSV leídos con éxito. Primeros registros:\n{df.head()}")

        # Cargar los datos en la base de datos
        session = Session()  # Crear una nueva sesión de base de datos
        for _, row in df.iterrows():
            store = Store(
                store_area=row['Store_Area'],
                items_available=row['Items_Available'],
                daily_customer_count=row['Daily_Customer_Count'],
                store_sales=row['Store_Sales']
            )
            session.add(store)
        session.commit()  # Confirmar los cambios
    except Exception as e:
        logging.error(f"Error al cargar el CSV: {e}")
    finally:
        session.close()  # Cerrar la sesión
        logging.info("Datos cargados correctamente en la base de datos.")

def get_db_session():
    """
    Retorna una nueva sesión de base de datos para ser utilizada en los servicios o controladores.
    """
    return Session()

# Cargar datos desde el CSV cuando la aplicación se inicia
load_data_from_csv()

