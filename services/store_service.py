from repositories.store_repository import StoreRepository
from models.store_model import Store
from sqlalchemy.orm import Session

"""
Librerías utilizadas:
- repositories.store_repository: Proporciona la clase StoreRepository para la gestión de tiendas en la base de datos.
- models.store_model: Define el modelo Store que representa la entidad de tienda.
- sqlalchemy.orm.Session: Permite manejar la sesión de la base de datos para realizar operaciones transaccionales.
"""

class StoreService:
    """
    Capa de servicios para la gestión de tiendas.
    Esta clase orquesta la lógica de negocio relacionada con las tiendas, utilizando el repositorio para acceder a los datos.
    Permite mantener la lógica de negocio separada de la capa de acceso a datos y de la base de datos.
    """
    def __init__(self, db_session: Session):
        """
        Inicializa el servicio de tiendas con una sesión de base de datos y un repositorio de tiendas.
        """
        self.repository = StoreRepository(db_session)

    def listar_tiendas(self):
        """
        Recupera y retorna todas las tiendas registradas en el sistema.
        Utiliza el repositorio para obtener la lista completa de tiendas.
        Es útil para mostrar catálogos o listados generales de tiendas.
        """
        return self.repository.get_all_stores()

    def obtener_tienda(self, store_id: int):
        """
        Busca y retorna una tienda específica por su identificador único (ID).
        Utiliza el repositorio para acceder a la tienda correspondiente.
        Es útil para mostrar detalles o realizar operaciones sobre una tienda concreta.
        """
        return self.repository.get_store_by_id(store_id)

    def crear_tienda(self, store_area: float, items_available: int, daily_customer_count: int, store_sales: float):
        """
        Crea una nueva tienda con los parámetros proporcionados.
        Utiliza el repositorio para almacenar la nueva tienda en la base de datos.
        Es útil para registrar nuevas tiendas en el sistema.
        """
        return self.repository.create_store(store_area, items_available, daily_customer_count, store_sales)

    def actualizar_tienda(self, store_id: int, store_area: float = None, items_available: int = None, 
                          daily_customer_count: int = None, store_sales: float = None):
        """
        Actualiza la información de una tienda existente, permitiendo modificar su área, artículos disponibles,
        clientes diarios y ventas.
        Utiliza el repositorio para realizar la actualización en la base de datos.
        Es útil para mantener actualizada la información de las tiendas.
        """
        return self.repository.update_store(store_id, store_area, items_available, daily_customer_count, store_sales)

    def eliminar_tienda(self, store_id: int):
        """
        Elimina una tienda del sistema según su identificador único (ID).
        Utiliza el repositorio para eliminar la tienda de la base de datos.
        Es útil para operaciones administrativas o de mantenimiento.
        """
        return self.repository.delete_store(store_id)
