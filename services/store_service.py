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

    def listar_tiendas_paginadas(self, page, per_page):
        """
        Lista tiendas con paginación.
        :param page: Número de página (empezando desde 1).
        :param per_page: Número de elementos por página.
        :return: Diccionario con datos paginados y metadatos.
        """
        try:
            # Calcular offset
            offset = (page - 1) * per_page
            
            # Obtener el total de registros
            total = self.session.query(Store).count()
            
            # Obtener los registros paginados
            stores = self.session.query(Store).offset(offset).limit(per_page).all()
            
            # Calcular metadatos de paginación
            total_pages = (total + per_page - 1) // per_page  # Ceiling division
            has_prev = page > 1
            has_next = page < total_pages
            
            # Preparar respuesta
            result = {
                'stores': [store.to_dict() for store in stores],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_prev': has_prev,
                    'has_next': has_next,
                    'prev_page': page - 1 if has_prev else None,
                    'next_page': page + 1 if has_next else None
                }
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error al obtener tiendas paginadas: {e}")
            return {
                'stores': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'total_pages': 0,
                    'has_prev': False,
                    'has_next': False,
                    'prev_page': None,
                    'next_page': None
                }
            }

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

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas generales de las tiendas.
        :return: Diccionario con estadísticas.
        """
        try:
            from sqlalchemy import func
            
            # Obtener estadísticas básicas
            stats = self.session.query(
                func.count(Store.store_id).label('total_stores'),
                func.avg(Store.store_area).label('avg_store_area'),
                func.avg(Store.items_available).label('avg_items_available'),
                func.avg(Store.daily_customer_count).label('avg_daily_customers'),
                func.avg(Store.store_sales).label('avg_store_sales'),
                func.sum(Store.store_sales).label('total_sales'),
                func.max(Store.store_sales).label('max_sales'),
                func.min(Store.store_sales).label('min_sales')
            ).first()
            
            # Formatear resultados
            result = {
                'total_stores': stats.total_stores or 0,
                'averages': {
                    'store_area': round(float(stats.avg_store_area or 0), 2),
                    'items_available': round(float(stats.avg_items_available or 0), 2),
                    'daily_customers': round(float(stats.avg_daily_customers or 0), 2),
                    'store_sales': round(float(stats.avg_store_sales or 0), 2)
                },
                'sales': {
                    'total': round(float(stats.total_sales or 0), 2),
                    'maximum': round(float(stats.max_sales or 0), 2),
                    'minimum': round(float(stats.min_sales or 0), 2),
                    'average': round(float(stats.avg_store_sales or 0), 2)
                }
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error al obtener estadísticas: {e}")
            return {
                'total_stores': 0,
                'averages': {'store_area': 0, 'items_available': 0, 'daily_customers': 0, 'store_sales': 0},
                'sales': {'total': 0, 'maximum': 0, 'minimum': 0, 'average': 0}
            }
