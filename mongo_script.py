from pymongo import MongoClient
from datetime import datetime
from pprint import pprint # Para imprimir documentos de forma más legible

# --- 1. Configuración de la Conexión a MongoDB Atlas ---
# ¡LÍNEA ACTUALIZADA CON TU NUEVA CADENA DE CONEXIÓN!
MONGO_URI = 'mongodb+srv://clasesunivalle001:PoDcHnBh13FC7vTI@cluster0.2eo714p.mongodb.net/'

try:
    cliente = MongoClient(MONGO_URI)
    # Ping para verificar la conexión
    cliente.admin.command('ping')
    print("Conexión exitosa a MongoDB Atlas.")

    # Si tu URI no especifica la base de datos, la seleccionas aquí.
    # Usaremos 'jardineria_clases01' como lo habías indicado antes,
    # a menos que quieras trabajar con otra base de datos en este clúster.
    db = cliente['jardineria_clases01']


    print("\nColecciones en la base de datos 'jardineria_clases01':")
    print(db.list_collection_names())

    # --- 2. Operaciones de Inserción (ejemplo con 'oficinas_nuevo') ---
    print("\n--- Operaciones con 'oficinas_nuevo' ---")
    oficina_collection = db['oficinas_nuevo']

    # Opcional: Eliminar documentos existentes para empezar limpio (solo para pruebas)
    # oficina_collection.delete_many({})
    # print("Documentos existentes en 'oficinas_nuevo' eliminados.")

    # Insertar varios documentos
    oficina_collection.insert_many([
        {'nombre': 'oficina1', 'direccion': 'calle1'},
        {'nombre': 'oficina2', 'direccion': 'calle2'},
        {'nombre': 'oficina3', 'direccion': 'calle3'},
        {'nombre': 'oficina4', 'direccion': 'calle4'}
    ])
    print("Documentos insertados en 'oficinas_nuevo'.")

    print("\nDocumentos en la colección 'oficinas_nuevo':")
    for doc in oficina_collection.find():
        pprint(doc)

    # --- 3. Obtener valores distintos de 'estado' en la colección 'pedido' ---
    print("\n--- Estados distintos de pedidos ---")
    pedido_collection = db['pedido'] # Asegúrate de que esta colección existe

    if 'pedido' in db.list_collection_names():
        estado_pedido = pedido_collection.distinct('estado')
        print("Estados de pedidos distintos:")
        for estado in estado_pedido:
            print(estado)
    else:
        print("La colección 'pedido' no existe en la base de datos.")


    # --- 4. Consultar pedidos con 'estado' y 'fechapedido' en un rango ---
    print("\n--- Pedidos rechazados en un rango de fechas (2009-01-01 a 2009-02-01) ---")
    if 'pedido' in db.list_collection_names():
        estado_pedido_filtrado = pedido_collection.find(
            {
                "estado": "Rechazado",
                "fechapedido": {
                    "$gte": datetime(2009, 1, 1),
                    "$lte": datetime(2009, 2, 1, 23, 59, 59)
                }
            }
        )
        found_any = False
        for pedido in estado_pedido_filtrado:
            pprint(pedido)
            found_any = True
        if not found_any:
            print("No se encontraron pedidos rechazados en el rango de fechas especificado.")
    else:
        print("La colección 'pedido' no existe para la consulta de fecha.")

    # --- 5. Realizar una Agregación (Lookup) de clientes y pedidos ---
    print("\n--- Agregación: Clientes con sus pedidos ---")
    cliente_collection = db['cliente'] # Asegúrate de que esta colección existe

    if 'cliente' in db.list_collection_names() and 'pedido' in db.list_collection_names():
        # Tu pipeline de agregación original
        pipeline = [
            {
                "$lookup": {
                    "from": 'pedido',         # Colección con la que unir
                    "localField": 'codigocliente', # Campo en la colección 'cliente'
                    "foreignField": 'idcliente',  # Campo en la colección 'pedido'
                    "as": 'pedidos'           # Nombre del nuevo campo con los documentos unidos
                }
            },
            {
                "$unwind": {
                    "path": '$pedidos',
                    "preserveNullAndEmptyArrays": True # Mantiene clientes sin pedidos
                }
            },
            # Opcional: Proyección para seleccionar solo los campos que te interesan
            # {
            #     "$project": {
            #         "_id": 0,
            #         "nombre_cliente": "$nombre",
            #         "codigo_cliente": "$codigocliente",
            #         "pedido_estado": "$pedidos.estado",
            #         "pedido_fecha": "$pedidos.fechapedido",
            #         "pedido_total": "$pedidos.total"
            #     }
            # }
        ]
        
        clientes_con_pedidos = cliente_collection.aggregate(pipeline)
        
        found_any = False
        for doc in clientes_con_pedidos:
            pprint(doc)
            found_any = True
        if not found_any:
            print("No se encontraron resultados para la agregación de clientes y pedidos.")
    else:
        print("Las colecciones 'cliente' o 'pedido' no existen para la agregación.")

except Exception as e:
    print(f"Error al conectar o interactuar con MongoDB: {e}")
finally:
    # Cierra la conexión cuando termines
    if 'cliente' in locals() and cliente is not None:
        cliente.close()
        print("\nConexión a MongoDB cerrada.")