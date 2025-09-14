import logging
import socketio
from utils import save_to_file
from config import BASE_URL, INSTANCE, API_KEY

sio = socketio.AsyncClient()

# Guardamos en dos archivos distintos
POLL_FILE = "presentes.json"
CAUSAS_FILE = "causas.json"

@sio.event
async def connect():
    logging.info("✅ Conectado al WebSocket de EvolutionAPI")

@sio.event
async def disconnect():
    logging.warning("❌ Desconectado del WebSocket")

@sio.on("messages.upsert")
async def handle_message(data):
    try:
        msg = data["data"]
        user = msg["key"]["remoteJid"]
        pushName = msg.get("pushName", "Desconocido")

        # 1) Si es respuesta al poll
        if "pollUpdateMessage" in msg.get("message", {}):
            options = msg["message"]["pollUpdateMessage"]["vote"]["selectedOptions"]
            opcion = options[0]["optionName"] if options else "Sin opción"
            logging.info(f"🗳 {pushName} votó: {opcion}")
            save_to_file(POLL_FILE, user, {"nombre": pushName, "estado": "PRESENTE"})

        # 2) Si es mensaje privado con causa
        elif "conversation" in msg.get("message", {}):
            text = msg["message"]["conversation"]
            logging.info(f"💬 {pushName} causa: {text}")
            save_to_file(CAUSAS_FILE, user, {"nombre": pushName, "estado": "AUSENTE_CON_CAUSA"})

    except Exception as e:
        logging.error(f"⚠️ Error procesando mensaje: {e}")

async def start_listener():
    await sio.connect(f"{BASE_URL}/{INSTANCE}", headers={"apikey": API_KEY}, transports=["websocket"])
    await sio.wait()
