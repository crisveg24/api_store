import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models.store_model import Base  # Importamos Base desde el modelo de Store
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
Base.metadata.create_all(engine)  # Crea las tablas en la base de datos

def get_db_session():
    """
    Retorna una nueva sesión de base de datos para ser utilizada en los servicios o controladores.
    """
    return Session()
