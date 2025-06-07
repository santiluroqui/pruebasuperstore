# scripts/load_csv.py
import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.base import engine
from models.model import SuperstoreSale
import datetime
from pandas import NaT # Importamos NaT para la comparación

# URL del archivo CSV de Superstore
CSV_URL = 'https://raw.githubusercontent.com/rudyluis/DashboardJS/main/superstore_data.csv'

def load_data_to_db():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print(f"Intentando cargar datos desde: {CSV_URL}")
        df = pd.read_csv(CSV_URL, encoding='latin1')
        print(f"CSV cargado. Filas: {len(df)}")
        
        print("Columnas en el CSV:", df.columns.tolist()) 

        # === VERIFICACIONES ACTUALIZADAS BASADAS EN LA SALIDA DE TU CSV ===
        if 'OrderDate' not in df.columns:
            raise ValueError("Columna 'OrderDate' no encontrada en el CSV.")
        if 'ShipDate' not in df.columns:
            raise ValueError("Columna 'ShipDate' no encontrada en el CSV.")
        if 'OrderID' not in df.columns:
            raise ValueError("Columna 'OrderID' no encontrada en el CSV.")
        if 'ProductName' not in df.columns:
            raise ValueError("Columna 'ProductName' no encontrada en el CSV.")
        if 'Postal Code' not in df.columns: # Mantén este check
            print("Advertencia: Columna 'Postal Code' no encontrada. Se procederá sin ella o con valores predeterminados.")
            df['Postal Code'] = 0 

        # Convertir columnas de fecha a datetime.datetime
        print("Procesando columna 'OrderDate'...")
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], format='%d/%m/%Y', errors='coerce')
        
        print("Procesando columna 'ShipDate'...")
        df['ShipDate'] = pd.to_datetime(df['ShipDate'], format='%d/%m/%Y', errors='coerce')

        print("Procesando columna 'Postal Code'...")
        df['Postal Code'] = pd.to_numeric(df['Postal Code'], errors='coerce').fillna(0).astype(int)

        print("Iniciando inserción de datos en la base de datos...")
        
        for index, row in df.iterrows():
            try:
                # === MODIFICACIÓN CLAVE AQUÍ: MANEJO DE NaT ===
                order_date_val = row['OrderDate'] if pd.notna(row['OrderDate']) else None
                ship_date_val = row['ShipDate'] if pd.notna(row['ShipDate']) else None

                sale = SuperstoreSale(
                    order_id=row['OrderID'],
                    order_date=order_date_val, # Usar el valor manejado para NaT
                    ship_date=ship_date_val,   # Usar el valor manejado para NaT
                    ship_mode=row['ShipMode'],
                    customer_id=row['CustomerID'],
                    customer_name=row['CustomerName'],
                    segment=row['Segment'],
                    country=row['Country'],
                    city=row['City'],
                    state=row['State'],
                    postal_code=row['Postal Code'], 
                    region=row['Region'],
                    product_id=row['ProductID'],
                    category=row['Category'],
                    sub_category=row['Sub-Category'],
                    product_name=row['ProductName'],
                    sales=row['Sales'],
                    quantity=row['Quantity'],
                    discount=row['Discount'],
                    profit=row['Profit']
                )
                session.add(sale)
                # Aquí se sigue haciendo el commit cada 1000 filas.
                # Si el error persiste en filas específicas, podríamos hacer commit por fila
                # para identificar mejor la fila que falla, pero ralentizaría mucho el proceso.
                if index % 1000 == 0: 
                    session.commit()
                    print(f"Insertadas {index} filas...")
            except Exception as row_e:
                print(f"Error al procesar la fila {index} (Order ID: {row.get('OrderID', 'N/A')}): {row_e}")
                # Aquí se hace un rollback por cada error de fila, lo que podría no ser óptimo
                # si quieres insertar la mayoría de los datos. Para depuración es útil.
                session.rollback() 
                continue 
        
        # Este commit final es crucial para los datos del último lote o si no hubo errores.
        try:
            session.commit()
            print(f"¡Datos de Superstore cargados exitosamente en la tabla 'superstore_sales'!")
        except Exception as final_commit_e:
            session.rollback()
            print(f"Error en el commit final: {final_commit_e}")

    except Exception as e:
        session.rollback()
        print(f"Error crítico al cargar datos en la base de datos: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Asegúrate de limpiar la tabla antes de cada carga si estás depurando,
        # para evitar problemas de claves primarias duplicadas si algunas filas pasaron antes.
        session.query(SuperstoreSale).delete()
        session.commit()
        print("Tabla 'superstore_sales' limpiada antes de la carga.")
    except Exception as e:
        session.rollback()
        print(f"Error al limpiar la tabla 'superstore_sales': {e}")
    finally:
        session.close()

    load_data_to_db()