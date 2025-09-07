from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""
La clase Store representa una tienda dentro del sistema. Cada instancia de esta clase corresponde a una tienda específica, 
almacenando información relevante como el área de la tienda, el número de artículos disponibles, el número de clientes diarios 
y las ventas de la tienda. Esta clase está mapeada a la tabla 'stores' en la base de datos y permite gestionar la información 
de las tiendas.
"""
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
        return {
            'store_id': self.store_id,
            'store_area': self.store_area,
            'items_available': self.items_available,
            'daily_customer_count': self.daily_customer_count,
            'store_sales': self.store_sales
        }
