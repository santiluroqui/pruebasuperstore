# models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ¡MUY IMPORTANTE!: Reemplaza 'user', 'password' y 'your_database_name' con tus credenciales reales.
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/superstore"

engine = create_engine(DATABASE_URL)
Base = declarative_base()