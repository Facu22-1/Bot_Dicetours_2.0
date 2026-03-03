import os
import json
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq

# Importamos tu motor de búsqueda local
from busqueda_micros import buscar_opciones

# ==========================================
# 1. CONFIGURACIÓN DE APIs
# ==========================================
# Si lo estás corriendo de prueba en la notebook, podés poner tus claves 
# entre comillas acá temporalmente, pero ¡acordate de borrarlas antes de subir a GitHub!
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "ACA_VA_TU_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "ACA_VA_TU_API_KEY")

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
# 2. EL CEREBRO CENTRAL (Procesa el texto final)
# ==========================================
async def responder_consulta(update: Update, texto_usuario: str):
    tz = pytz.timezone('America/Argentina/Mendoza')
    hora_actual = datetime.now(tz).strftime("%H:%M")
    
    try:
        # Petición a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": texto_usuario}
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.0,
            response_format={"type": "json_object"} 
        )
        
        datos_ia = json.loads(chat_completion.choices[0].message.content)
        
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
        
        # El encabezado ahora incluye lo que el bot escuchó/leyó
        header = f"🗣️ Entendí: \"{texto_usuario.capitalize()}\"\n🗺️ Viaje: {origen} ➡️ {destino}\n⏱️ Hora de cálculo: {hora_actual}\n\n"
        cuerpo_mensaje = "\n\n➖➖➖➖➖➖➖➖➖➖\n\n".join(respuestas)
        
        await update.message.reply_text(header + cuerpo_mensaje)
        
    except Exception as e:
        print(f"Error interno: {e}")
        await update.message.reply_text("🚨 Che, hubo un error interno procesando los datos. Intentá de nuevo.")

# ==========================================
# 3. LOS OÍDOS (Handlers de Telegram)
# ==========================================
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Buscando horarios...")
    await responder_consulta(update, update.message.text)

async def procesar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Escuchando el audio...")
    
    # Descargamos el archivo de voz temporalmente
    archivo = await context.bot.get_file(update.message.voice.file_id)
    ruta_audio = "audio_temp.ogg"
    await archivo.download_to_drive(ruta_audio)

    try:
        # Groq Whisper hace la magia de transcribir
        with open(ruta_audio, "rb") as f:
            transcripcion = client.audio.transcriptions.create(
                file=(ruta_audio, f.read()),
                model="whisper-large-v3",
                language="es" 
            )
        
        texto_hablado = transcripcion.text
        os.remove(ruta_audio) # Limpiamos la basura
        
        # Le pasamos el texto limpio a nuestro cerebro central
        await responder_consulta(update, texto_hablado)

    except Exception as e:
        print(f"Error con el audio: {e}")
        await update.message.reply_text("🚨 No pude escuchar bien el audio. ¿Me lo escribís?")

# ==========================================
# 4. ARRANQUE DEL SERVIDOR
# ==========================================
def main():
    print("Iniciando Dicetours Bot con soporte de notas de voz...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Le decimos que preste atención tanto a texto como a notas de voz
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))
    app.add_handler(MessageHandler(filters.VOICE, procesar_audio))
    
    print("✅ ¡Bot 100% operativo escuchando y leyendo!")
    app.run_polling()

if __name__ == "__main__":
    main()
