import os
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models.store_model import Base, Store  
from models.user_model import User  # Importar modelo de usuario
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
        engine = create_engine(SQLITE_URI, echo=False)  # Cambiado a False para menos logs
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

def create_tables():
    """
    Crear todas las tablas en la base de datos.
    """
    try:
        # Crear todas las tablas definidas en Base
        Base.metadata.create_all(engine)
        logging.info("Todas las tablas creadas exitosamente")
    except Exception as e:
        logging.error(f"Error al crear tablas: {e}")
        raise

def get_session():
    """
    Retorna una nueva sesión de base de datos para ser utilizada en los servicios o repositorios.
    """
    return Session()

def load_data_from_csv():
    """
    Carga los datos desde el archivo CSV a la base de datos.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'files', 'Stores_clean.csv')  
    logging.info(f"Archivo CSV localizado en: {file_path}")

    session = None  # Inicializa la variable 'session'

    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        logging.info(f"Datos del CSV leídos con éxito. Total de registros: {len(df)}")

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
        logging.info("Datos cargados correctamente en la base de datos.")
        
    except Exception as e:
        logging.error(f"Error al cargar el CSV: {e}")
        if session:
            session.rollback()
    finally:
        # Cerrar la sesión solo si fue abierta
        if session:
            session.close()

def get_db_session():
    """
    Función legacy para compatibilidad.
    Usa get_session() en su lugar.
    """
    return get_session()

def initialize_data():
    """
    Carga datos desde CSV solo si la base de datos está vacía.
    También crea el usuario administrador por defecto si no existe.
    """
    session = Session()
    try:
        # Verificar si ya existen datos de tiendas
        store_count = session.query(Store).count()
        if store_count == 0:
            logging.info("Base de datos de tiendas vacía. Cargando datos desde CSV...")
            load_data_from_csv()
        else:
            logging.info(f"Base de datos ya contiene {store_count} tiendas. Omitiendo carga de CSV.")
        
        # Verificar y crear usuario administrador por defecto
        user_count = session.query(User).count()
        
        # Importar UserRole correctamente
        from models.user_model import UserRole
        admin_count = session.query(User).filter_by(role=UserRole.ADMIN).count()
        
        if admin_count == 0:
            logging.info("No existe usuario administrador. Creando admin por defecto...")
            from utils.auth_utils import hash_password
            
            admin_user = User(
                username='admin',
                email='admin@tiendas.com',
                password_hash=hash_password('admin123'),
                role=UserRole.ADMIN,
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            logging.info("✅ Usuario administrador creado: admin/admin123")
        else:
            logging.info(f"Sistema cuenta con {admin_count} administrador(es) existente(s)")
        
        logging.info(f"Base de datos contiene {user_count} usuarios totales.")
        
    except Exception as e:
        logging.error(f"Error al inicializar datos: {e}")
        session.rollback()
    finally:
        session.close()

# NO inicializar datos al importar el módulo para evitar problemas de orden
# La inicialización se hará desde Main.py

