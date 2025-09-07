from models.store_model import Store
from sqlalchemy.orm import Session
import logging

class StoreService:
    def __init__(self, session: Session):
        """
        Constructor del servicio Store.
        """
        self.session = session

    def listar_tiendas(self):
        """
        Lista todas las tiendas en la base de datos.
        :return: Lista de objetos Store.
        """
        try:
            return self.session.query(Store).all()
        except Exception as e:
            logging.error(f"Error al obtener tiendas: {e}")
            return []

    def crear_tienda(self, store_area, items_available, daily_customer_count, store_sales):
        """
        Crea una nueva tienda en la base de datos.
        :param store_area: Área de la tienda (float).
        :param items_available: Número de artículos disponibles (int).
        :param daily_customer_count: Número de clientes diarios (int).
        :param store_sales: Ventas diarias de la tienda (float).
        :return: Objeto Store creado.
        """
        try:
            store = Store(
                store_area=store_area,
                items_available=items_available,
                daily_customer_count=daily_customer_count,
                store_sales=store_sales
            )
            self.session.add(store)
            self.session.commit()  # Guardamos los cambios en la base de datos
            return store
        except Exception as e:
            logging.error(f"Error al crear la tienda: {e}")
            self.session.rollback()  # Deshacer cambios en caso de error
            return None

    def obtener_tienda(self, store_id):
        """
        Obtiene una tienda específica por su ID.
        :param store_id: ID de la tienda a obtener (int).
        :return: Objeto Store si existe, None si no existe.
        """
        try:
            return self.session.query(Store).filter(Store.store_id == store_id).first()
        except Exception as e:
            logging.error(f"Error al obtener la tienda con ID {store_id}: {e}")
            return None

    def actualizar_tienda(self, store_id, store_area=None, items_available=None, 
                          daily_customer_count=None, store_sales=None):
        """
        Actualiza la información de una tienda existente.
        :param store_id: ID de la tienda a actualizar (int).
        :param store_area: Nueva área de la tienda (float).
        :param items_available: Nuevo número de artículos disponibles (int).
        :param daily_customer_count: Nuevo número de clientes diarios (int).
        :param store_sales: Nuevas ventas diarias de la tienda (float).
        :return: Objeto Store actualizado, None si no se encuentra la tienda.
        """
        try:
            store = self.session.query(Store).filter(Store.store_id == store_id).first()
            if store:
                if store_area is not None:
                    store.store_area = store_area
                if items_available is not None:
                    store.items_available = items_available
                if daily_customer_count is not None:
                    store.daily_customer_count = daily_customer_count
                if store_sales is not None:
                    store.store_sales = store_sales
                self.session.commit()  # Guardamos los cambios
                self.session.refresh(store)
                return store
            else:
                logging.warning(f"Tienda con ID {store_id} no encontrada para actualizar.")
                return None
        except Exception as e:
            logging.error(f"Error al actualizar la tienda con ID {store_id}: {e}")
            self.session.rollback()  # Deshacer cambios en caso de error
            return None

    def eliminar_tienda(self, store_id):
        """
        Elimina una tienda de la base de datos.
        :param store_id: ID de la tienda a eliminar (int).
        :return: True si la tienda fue eliminada, False si no se encuentra.
        """
        try:
            store = self.session.query(Store).filter(Store.store_id == store_id).first()
            if store:
                self.session.delete(store)
                self.session.commit()  # Confirmamos la eliminación
                return True
            else:
                logging.warning(f"Tienda con ID {store_id} no encontrada para eliminar.")
                return False
        except Exception as e:
            logging.error(f"Error al eliminar la tienda con ID {store_id}: {e}")
            self.session.rollback()  # Deshacer cambios en caso de error
            return False
