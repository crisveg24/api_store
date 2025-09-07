import base64
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Store(Base):
    __tablename__ = 'stores'

    store_id = Column(Integer, primary_key=True, index=True)
    store_area = Column(Float, nullable=False)
    items_available = Column(Integer, nullable=False)
    daily_customer_count = Column(Integer, nullable=False)
    store_sales = Column(Float, nullable=False)

    def __init__(self, store_area, items_available, daily_customer_count, store_sales):
        self.store_area = store_area
        self.items_available = items_available
        self.daily_customer_count = daily_customer_count
        self.store_sales = store_sales

    def to_dict(self):
        """
        Convierte el objeto Store a un diccionario serializable en JSON.
        Si en el futuro hay atributos con tipos no serializables (como imágenes en bytes),
        los convierte a un formato adecuado (por ejemplo, base64).
        :return: Diccionario con los atributos de la tienda.
        """
        store_dict = {
            'store_id': self.store_id,
            'store_area': self.store_area,
            'items_available': self.items_available,
            'daily_customer_count': self.daily_customer_count,
            'store_sales': self.store_sales
        }
        # Convertir cualquier campo tipo bytes a base64
        for k, v in store_dict.items():
            if isinstance(v, bytes):
                store_dict[k] = base64.b64encode(v).decode('utf-8')
        return store_dict
