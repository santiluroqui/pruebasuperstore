# scripts/create_database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base, DATABASE_URL # Importa Base y DATABASE_URL del archivo base.py
from models.model import Usuario, SuperstoreSale # Importa todos tus modelos definidos

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    print(f"Intentando conectar a la base de datos: {DATABASE_URL.split('@')[-1]}")
    try:
        # Crea todas las tablas que son subclases de Base.
        # Esto incluye 'usuarios' y 'superstore_sales'.
        Base.metadata.create_all(engine)
        print("¡Base de datos y tablas creadas/actualizadas exitosamente!")
    except Exception as e:
        print(f"Error al crear la base de datos o las tablas: {e}")
        print("Asegúrate de que el servidor PostgreSQL esté corriendo, las credenciales sean correctas y la base de datos exista.")

if __name__ == "__main__":
    create_db_and_tables()
    