import sqlite3

def crear_base_datos():
    # Nos conectamos a la base de datos (se crea automáticamente si no existe)
    conexion = sqlite3.connect("dicetours.db")
    cursor = conexion.cursor()

    # Borramos la tabla si existe para cargar los datos limpios y evitar duplicados
    cursor.execute('DROP TABLE IF EXISTS horarios')

    # Creamos la estructura definitiva
    cursor.execute('''
        CREATE TABLE horarios (
            id_viaje INTEGER PRIMARY KEY AUTOINCREMENT,
            origen TEXT,
            destino TEXT,
            hora_salida TEXT,
            hora_llegada TEXT,
            recorrido TEXT
        )
    ''')

    # --- LISTA COMPLETA DE HORARIOS ---
    # Formato: (Origen, Destino, Salida, Llegada, Recorrido)
    
    horarios = [
        # ==========================================
        # IDA (Rivadavia -> Facultad)
        # ==========================================
        
        # --- Ruta 60 ---
        ("Rivadavia", "Facultad", "06:05", "07:55", "Ruta 60"),
        ("Rivadavia", "Facultad", "11:05", "12:55", "Ruta 60"),
        ("Rivadavia", "Facultad", "16:00", "17:50", "Ruta 60"),
        ("Rivadavia", "Facultad", "20:15", "22:05", "Ruta 60"),

        # --- Barriales ---
        ("Rivadavia", "Facultad", "05:55", "07:45", "Barriales"),
        ("Rivadavia", "Facultad", "06:50", "08:40", "Barriales"),
        ("Rivadavia", "Facultad", "11:15", "13:05", "Barriales"),
        ("Rivadavia", "Facultad", "12:10", "14:00", "Barriales"),
        ("Rivadavia", "Facultad", "16:30", "18:20", "Barriales"),
        ("Rivadavia", "Facultad", "17:35", "19:25", "Barriales"),
        ("Rivadavia", "Facultad", "20:30", "22:20", "Barriales"),

        # --- San Martín ---
        ("Rivadavia", "Facultad", "06:00", "07:45", "San Martin"),
        ("Rivadavia", "Facultad", "07:00", "08:50", "San Martin"),
        ("Rivadavia", "Facultad", "08:20", "10:05", "San Martin"),
        ("Rivadavia", "Facultad", "09:20", "11:05", "San Martin"),
        ("Rivadavia", "Facultad", "10:20", "12:05", "San Martin"),
        ("Rivadavia", "Facultad", "12:15", "14:00", "San Martin"),
        ("Rivadavia", "Facultad", "14:10", "15:55", "San Martin"),
        ("Rivadavia", "Facultad", "15:10", "16:55", "San Martin"),
        ("Rivadavia", "Facultad", "16:20", "18:05", "San Martin"),
        ("Rivadavia", "Facultad", "18:05", "19:50", "San Martin"),
        ("Rivadavia", "Facultad", "19:20", "21:05", "San Martin"),
        ("Rivadavia", "Facultad", "20:10", "21:55", "San Martin"),

        # ==========================================
        # VUELTA (Facultad -> Rivadavia)
        # ==========================================
        
        # --- Ruta 60 ---
        ("Facultad", "Rivadavia", "08:05", "09:55", "Ruta 60"),
        ("Facultad", "Rivadavia", "13:00", "14:50", "Ruta 60"),
        ("Facultad", "Rivadavia", "18:00", "19:50", "Ruta 60"),
        ("Facultad", "Rivadavia", "22:25", "00:00", "Ruta 60"),

        # --- Barriales ---
        ("Facultad", "Rivadavia", "08:10", "10:00", "Barriales"),
        ("Facultad", "Rivadavia", "09:00", "10:50", "Barriales"), 
        ("Facultad", "Rivadavia", "13:30", "15:20", "Barriales"),
        ("Facultad", "Rivadavia", "14:30", "16:20", "Barriales"),
        ("Facultad", "Rivadavia", "18:30", "20:20", "Barriales"),
        ("Facultad", "Rivadavia", "20:10", "22:00", "Barriales"),
        ("Facultad", "Rivadavia", "22:30", "00:05", "Barriales"),

        # --- San Martín ---
        ("Facultad", "Rivadavia", "08:00", "09:45", "San Martin"),
        ("Facultad", "Rivadavia", "09:00", "10:45", "San Martin"),
        ("Facultad", "Rivadavia", "10:20", "12:05", "San Martin"),
        ("Facultad", "Rivadavia", "11:20", "13:05", "San Martin"),
        ("Facultad", "Rivadavia", "12:15", "14:00", "San Martin"),
        ("Facultad", "Rivadavia", "14:05", "15:50", "San Martin"),
        ("Facultad", "Rivadavia", "16:00", "17:45", "San Martin"),
        ("Facultad", "Rivadavia", "17:00", "18:45", "San Martin"),
        ("Facultad", "Rivadavia", "18:10", "19:55", "San Martin"),
        ("Facultad", "Rivadavia", "20:15", "22:00", "San Martin"),
        ("Facultad", "Rivadavia", "21:05", "22:50", "San Martin"),
        ("Facultad", "Rivadavia", "22:00", "23:45", "San Martin"),
    ]

    # Insertamos todos los datos de forma masiva
    cursor.executemany('''
        INSERT INTO horarios (origen, destino, hora_salida, hora_llegada, recorrido)
        VALUES (?, ?, ?, ?, ?)
    ''', horarios)

    conexion.commit()
    conexion.close()
    print("¡Base de datos 'dicetours.db' creada exitosamente con todos los horarios!")

if __name__ == "__main__":
    crear_base_datos()