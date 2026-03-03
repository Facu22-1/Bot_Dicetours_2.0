import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================================
# 1. TUS CLAVES
# ==========================================
# Reemplazá esto por las claves que sacaste de BotFather y AI Studio
TELEGRAM_TOKEN = "8469178246:AAGGwrgvUOZi_eMXxZdstFLpAcEFoql_2-g"
GEMINI_API_KEY = "AIzaSyBlULIvQo76iRZYROgrD0cT8pjqTI6sbFg"

# ==========================================
# 2. PRUEBA DE GEMINI
# ==========================================
print("⏳ Conectando con el cerebro de Gemini...")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    modelo = genai.GenerativeModel("gemini-2.5-flash")
    # Le pedimos algo simple para probar
    respuesta = modelo.generate_content("Decí 'Hola, conexión exitosa' en una sola línea.")
    print(f"✅ Gemini responde: {respuesta.text.strip()}")
except Exception as e:
    print(f"❌ Error conectando con Gemini: {e}")
    exit()

# ==========================================
# 3. PRUEBA DE TELEGRAM
# ==========================================
async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("¡Recibí un mensaje en Telegram!")
    await update.message.reply_text("¡Hola! Tu servidor Compaq y Telegram se están comunicando perfecto. 🚀")

print("\n⏳ Iniciando servidor de Telegram...")
try:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", comando_start))
    
    print("✅ ¡Bot online! Entrá a Telegram y mandale el comando /start")
    app.run_polling()
except Exception as e:
    print(f"❌ Error conectando con Telegram: {e}")