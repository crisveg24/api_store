from models.store_model import Store
from sqlalchemy.orm import Session

class StoreRepository:
    """
    Repositorio para la gestión de tiendas en la base de datos.
    Proporciona métodos para crear, consultar, actualizar y eliminar tiendas.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_stores(self):
        """
        Recupera todas las tiendas almacenadas en la base de datos.
        Utiliza una consulta ORM para obtener todas las instancias de la clase Store,
        permitiendo listar todas las tiendas registradas en el sistema.
        """
        return self.db.query(Store).all()

    def get_store_by_id(self, store_id: int):
        """
        Busca y retorna una tienda específica según su identificador único (ID).
        Realiza una consulta filtrando por el campo 'store_id' de la tabla Store.
        Devuelve la instancia de Store si existe, o None si no se encuentra.
        """
        return self.db.query(Store).filter(Store.store_id == store_id).first()

    def create_store(self, store_area: float, items_available: int, daily_customer_count: int, store_sales: float):
        """
        Crea y almacena una nueva tienda en la base de datos.
        Recibe parámetros como el área de la tienda, el número de artículos disponibles,
        el número de clientes diarios y las ventas diarias. Crea una nueva instancia de Store
        y la agrega a la sesión de la base de datos. Tras confirmar la transacción,
        retorna la nueva tienda creada, incluyendo su ID asignado automáticamente.
        """
        new_store = Store(store_area=store_area, items_available=items_available, 
                          daily_customer_count=daily_customer_count, store_sales=store_sales)
        self.db.add(new_store)
        self.db.commit()
        self.db.refresh(new_store)
        return new_store

    def update_store(self, store_id: int, store_area: float = None, items_available: int = None, 
                 daily_customer_count: int = None, store_sales: float = None):
        """
        Actualiza la información de una tienda existente, permitiendo modificar su área, artículos disponibles,
        clientes diarios y ventas.
        Utiliza el repositorio para realizar la actualización en la base de datos.
        Es útil para mantener actualizada la información de las tiendas.
        """
        store = self.get_store_by_id(store_id)
        if store:
            if store_area is not None:
                store.store_area = store_area
            if items_available is not None:
                store.items_available = items_available
            if daily_customer_count is not None:
                store.daily_customer_count = daily_customer_count
            if store_sales is not None:
                store.store_sales = store_sales
            self.db.commit()
            self.db.refresh(store)
        return store


    def delete_store(self, store_id: int):
        """
        Elimina una tienda de la base de datos según su identificador único (ID).
        Busca la tienda correspondiente y, si existe, la elimina de la base de datos.
        Confirma la transacción y devuelve la instancia de la tienda eliminada o None si
        no se encuentra.
        """
        store = self.get_store_by_id(store_id)
        if store:
            self.db.delete(store)
            self.db.commit()
        return store
