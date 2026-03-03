import sqlite3
from datetime import datetime

# ==========================================
# 1. FUNCIONES AUXILIARES (Matemática de tiempo)
# ==========================================

def a_minutos(hora_str):
    """Convierte 'HH:MM' a minutos totales. Maneja los micros de trasnoche."""
    h, m = map(int, hora_str.split(':'))
    minutos = h * 60 + m
    # Si la hora es entre 00:00 y 04:00, asumimos que es del día siguiente
    if h < 4:
        minutos += 1440
    return minutos

def ya_salio(hora_salida, hora_actual):
    """Compara si el micro ya se fue."""
    return a_minutos(hora_salida) < a_minutos(hora_actual)

# ==========================================
# 2. MOTOR DE BÚSQUEDA Y FILTRADO
# ==========================================

def buscar_opciones(caso, origen, destino, hora_actual, hora_ref=None, recorrido_pref=None):
    conexion = sqlite3.connect("dicetours.db")
    cursor = conexion.cursor()
    
    query = "SELECT hora_salida, hora_llegada, recorrido FROM horarios WHERE origen = ? AND destino = ?"
    params = [origen, destino]
    
    if recorrido_pref:
        query += " AND recorrido = ?"
        params.append(recorrido_pref)
        
    cursor.execute(query, params)
    todos_los_micros = cursor.fetchall()
    conexion.close()

    if not todos_los_micros:
        return ["No encontré micros para esa ruta."]

    resultados = []
    minutos_actual = a_minutos(hora_actual)
    minutos_ref = a_minutos(hora_ref) if hora_ref else 0

    # CASO 1: LLEGAR ALREDEDOR DE X HORA
    if caso == 1:
        micros_ordenados = sorted(todos_los_micros, key=lambda x: abs(a_minutos(x[1]) - minutos_ref))
        resultados = micros_ordenados[:3]

    # CASO 2: LLEGAR ANTES DE X HORA
    elif caso == 2:
        micros_validos = [m for m in todos_los_micros if a_minutos(m[1]) <= minutos_ref]
        # El mejor es el que llega más tarde (más cerca de tu límite), por eso reverse=True
        micros_ordenados = sorted(micros_validos, key=lambda x: a_minutos(x[1]), reverse=True)
        resultados = micros_ordenados[:3]

    # CASO 3: IRSE YA
    elif caso == 3:
        micros_validos = [m for m in todos_los_micros if a_minutos(m[0]) >= minutos_actual]
        micros_ordenados = sorted(micros_validos, key=lambda x: a_minutos(x[0]))
        resultados = micros_ordenados[:3]

    # CASO 4: SALIR ALREDEDOR DE X HORA
    elif caso == 4:
        micros_ordenados = sorted(todos_los_micros, key=lambda x: abs(a_minutos(x[0]) - minutos_ref))
        resultados = micros_ordenados[:3]
        
    # ==========================================
    # 3. NUEVO ARMADO DEL MENSAJE PARA TELEGRAM
    # ==========================================
    mensajes_bot = []
    
    # Usamos enumerate para saber cuál es el primer resultado (el mejor)
    for i, (salida, llegada, recorrido) in enumerate(resultados):
        advertencia = "\n⚠️ ¡Cuidado! Este micro ya salió." if ya_salio(salida, hora_actual) else ""
        
        # Le asignamos un "podio" visual para que quede clarísimo
        if i == 0:
            podio = "🥇 OPICIÓN IDEAL"
        elif i == 1:
            podio = "🥈 Alternativa 1"
        else:
            podio = "🥉 Alternativa 2"

        # Estructura limpia con saltos de línea
        mensaje = (
            f"{podio}\n"
            f"🚌 Recorrido: {recorrido}\n"
            f"🟢 Sale: {salida}\n"
            f"🏁 Llega: {llegada}{advertencia}"
        )
        mensajes_bot.append(mensaje)
        
    if not mensajes_bot:
        return ["No hay micros disponibles bajo esas condiciones."]
        
    return mensajes_bot

# ==========================================
# BLOQUE DE PRUEBA (Para simular)
# ==========================================
if __name__ == "__main__":
    # Supongamos que son las 14:05 en tu servidor
    HORA_ACTUAL_SIMULADA = "14:05"
    
    print("--- PRUEBA DE CASOS ---")
    print("Hora actual del sistema:", HORA_ACTUAL_SIMULADA)
    
    print("\n1. 'Quiero llegar alrededor de las 15:00 a la facu'")
    opciones = buscar_opciones(caso=1, origen="Rivadavia", destino="Facultad", hora_actual=HORA_ACTUAL_SIMULADA, hora_ref="15:00")
    for op in opciones: print(op)

    print("\n2. 'Quiero llegar antes de las 16:00 a la facu'")
    opciones = buscar_opciones(caso=2, origen="Rivadavia", destino="Facultad", hora_actual=HORA_ACTUAL_SIMULADA, hora_ref="16:00")
    for op in opciones: print(op)

    print("\n3. 'Me quiero ir YA a la facu'")
    opciones = buscar_opciones(caso=3, origen="Rivadavia", destino="Facultad", hora_actual=HORA_ACTUAL_SIMULADA)
    for op in opciones: print(op)

    print("\n4. 'Salgo de cursar a las 20:30, qué micro de vuelta me conviene?'")
    opciones = buscar_opciones(caso=4, origen="Facultad", destino="Rivadavia", hora_actual=HORA_ACTUAL_SIMULADA, hora_ref="20:30")
    for op in opciones: print(op)

    print("\n5. '¿Cuándo sale el próximo Barriales hacia la facu?'")
    opciones = buscar_opciones(
        caso=3, 
        origen="Rivadavia", 
        destino="Facultad", 
        hora_actual="14:05", 
        recorrido_pref="Barriales" # <--- ¡Acá está la magia!
    )
    for op in opciones: print(op)