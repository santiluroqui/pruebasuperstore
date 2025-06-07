# models/model.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from .base import Base # Asegúrate de que base.py esté en la misma carpeta 'models'

# Clase de Usuario (solo la definición de la tabla, SIN LÓGICA DE AUTENTICACIÓN ESPECÍFICA DE FLASK-LOGIN AQUÍ)
class Usuario(Base): 
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    # ¡LÍNEA CORREGIDA! Aumentado a 255 caracteres
    password = Column(String(255), nullable=False) 

    def __repr__(self):
        return '<Usuario %r>' % self.username

# El modelo de SuperstoreSale tal cual está en tu base de datos
class SuperstoreSale(Base):
    __tablename__ = 'superstore_orders' # Nombre de la tabla en la DB
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), nullable=False)
    order_date = Column(DateTime)
    ship_date = Column(DateTime)
    ship_mode = Column(String(50))
    customer_id = Column(String(50))
    customer_name = Column(String(100))
    segment = Column(String(50))
    country = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(Integer) 
    region = Column(String(50))
    product_id = Column(String(50))
    category = Column(String(50))
    sub_category = Column(String(50))
    product_name = Column(String(255))
    sales = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    profit = Column(Float)

    def __repr__(self):
        return f"<SuperstoreSale Order: {self.order_id}, Product: {self.product_name}>"