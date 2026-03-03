import json
import os
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from groq import Groq
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# --- PARCHE PARA RENDER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot OK")

def keep_alive():
    # Render te va a asignar un puerto automático
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
# --------------------------

# Importamos tu motor de búsqueda local
from busqueda_micros import buscar_opciones

# ==========================================
# 1. CONFIGURACIÓN DE APIs
# ==========================================
# Uso variables de entorno para no exponer las claves en el código
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Inicializamos el cliente de Groq
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_INSTRUCTION = """
Eres el cerebro de un bot de Telegram que clasifica intenciones de viaje en colectivo (empresa Dicetours).
El usuario viaja únicamente entre "Rivadavia" y la "Facultad" (UNCuyo).
Devuelve EXCLUSIVAMENTE un JSON válido con esta estructura: {"caso": int, "origen": str, "destino": str, "hora_ref": str o null, "recorrido_pref": str o null}.

REGLAS DE EXTRACCIÓN:
1. origen y destino: Solo pueden ser "Rivadavia" o "Facultad". (casa/Riva = Rivadavia, facu/universidad = Facultad).
2. hora_ref: Formato "HH:MM" (24hs). Si dice "a las 3", asume "15:00" por el contexto universitario. Si no hay hora, null.
3. recorrido_pref: Solo puede ser "Ruta 60", "Barriales", "San Martin" o null. (Si dice "la 60" es "Ruta 60", si dice "por el centro" es "San Martin").

CASOS DE INTENCIÓN:
Caso 1: LLEGAR ALREDEDOR DE una hora. (Ej: "Llego a las 15 a la facu").
Caso 2: LLEGAR ANTES DE una hora estricta. (Ej: "Tengo que estar sí o sí antes de las 16 en casa").
Caso 3: IRSE YA o busca el PRÓXIMO micro. (Ej: "Me quiero ir ya a la facu").
Caso 4: SALIR ALREDEDOR DE una hora. (Ej: "Salgo de cursar a las 16, qué micro me tomo?").
"""

# ==========================================
# 2. LÓGICA DE RECEPCIÓN DE MENSAJES
# ==========================================
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_usuario = update.message.text
    
    tz = pytz.timezone('America/Argentina/Mendoza')
    hora_actual = datetime.now(tz).strftime("%H:%M")
    
    await update.message.reply_text("🤖 Buscando horarios...")

    try:
        # Petición a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": mensaje_usuario}
            ],
            model="llama-3.1-8b-instant", # Modelo liviano y veloz de Meta
            temperature=0.0,
            response_format={"type": "json_object"} # Forzamos el JSON
        )
        
        # Extraemos la respuesta
        respuesta_ia = chat_completion.choices[0].message.content
        datos_ia = json.loads(respuesta_ia)
        
        caso = datos_ia.get("caso")
        origen = datos_ia.get("origen")
        destino = datos_ia.get("destino")
        hora_ref = datos_ia.get("hora_ref")
        recorrido_pref = datos_ia.get("recorrido_pref")
        
        if caso not in [1, 2, 3, 4] or origen not in ["Rivadavia", "Facultad"]:
            await update.message.reply_text("🤔 Mmm, no me quedó claro el recorrido. ¿Me lo decís de otra forma?")
            return

        respuestas = buscar_opciones(
            caso=caso,
            origen=origen,
            destino=destino,
            hora_actual=hora_actual,
            hora_ref=hora_ref,
            recorrido_pref=recorrido_pref
        )
        
        header = f"🗺️ Viaje: {origen} ➡️ {destino}\n⏱️ Hora de cálculo: {hora_actual}\n\n"
        cuerpo_mensaje = "\n\n➖➖➖➖➖➖➖➖➖➖\n\n".join(respuestas)
        mensaje_final = header + cuerpo_mensaje
        
        await update.message.reply_text(mensaje_final)
        
    except Exception as e:
        print(f"Error interno: {e}")
        await update.message.reply_text("🚨 Che, hubo un error interno procesando los datos. Intentá de nuevo.")

# ==========================================
# 3. ARRANQUE DEL SERVIDOR
# ==========================================
def main():
    keep_alive() # Para Render 
    print("Iniciando servidor principal con API de Groq...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))
    print("✅ ¡Bot 100% operativo y esperando tus mensajes!")
    app.run_polling()

if __name__ == "__main__":
    main()