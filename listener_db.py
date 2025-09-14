# listener_db.py
import asyncio
import logging
import json
import sqlite3
from datetime import datetime
import socketio
import os
from pytz import timezone


from dotenv import load_dotenv

from notificador import notificar_respuesta

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
INSTANCE = os.getenv("INSTANCE")
API_KEY = os.getenv("API_KEY")

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")

# --- Configuración SQLite ---
DB_FILE = "eventos.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fechahora TEXT,
        numero_salida TEXT,
        numero_llegada TEXT,
        tipo_evento TEXT,
        mensaje TEXT,
        id_mensaje TEXT,
        id_mensaje_respondido TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_event(evento):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO eventos (
            fechahora, numero_salida, numero_llegada,
            tipo_evento, mensaje, id_mensaje, id_mensaje_respondido
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        evento["fechahora"], evento["numero_salida"], evento["numero_llegada"],
        evento["tipo_evento"], evento["mensaje"], evento["id_mensaje"], evento["id_mensaje_respondido"]
    ))
    conn.commit()
    conn.close()
    # 🔔 Nueva llamada para confirmar al usuario
    notificar_respuesta(evento["numero_salida"], evento["mensaje"])

# --- Cliente Socket.IO ---
sio = socketio.AsyncClient()

BOT_NUMBER = "BOT"  # 👈 así queda más claro que es el bot

@sio.event
async def connect():
    logging.info("✅ Conectado al WebSocket de EvolutionAPI")

@sio.event
async def disconnect():
    logging.warning("❌ Desconectado del WebSocket")

# Solo escuchamos "messages.upsert"
@sio.on("messages.upsert")
async def on_messages_upsert(payload):
    try:
        d = payload.get("data", {})
        argentina_tz = timezone('America/Argentina/Buenos_Aires')
        fechahora = datetime.now(argentina_tz).strftime("%Y-%m-%d %H:%M:%S")

        id_mensaje = d.get("key", {}).get("id")
        id_mensaje_respondido = d.get("contextInfo", {}).get("stanzaId")

        # texto del mensaje
        mensaje = None
        msg = d.get("message", {})
        if "conversation" in msg:
            mensaje = msg["conversation"]
        elif "extendedTextMessage" in msg:
            mensaje = msg["extendedTextMessage"].get("text")
        elif "reactionMessage" in msg:
            mensaje = msg["reactionMessage"].get("text")
        elif "pollCreationMessageV3" in msg:
            mensaje = "[Encuesta creada]"
        else:
            mensaje = "[sin texto]"
        
        if mensaje and isinstance(mensaje, str):
            mensaje = mensaje.lower()
        
        remoteJid = d.get("key", {}).get("remoteJid", "")
        from_me = d.get("key", {}).get("fromMe", False)

        # salida / llegada
        if from_me:
            numero_salida = BOT_NUMBER
            numero_llegada = remoteJid.replace("@s.whatsapp.net", "")
        else:
            numero_salida = remoteJid.replace("@s.whatsapp.net", "")
            numero_llegada = BOT_NUMBER

        evento = {
            "fechahora": fechahora,
            "numero_salida": numero_salida,
            "numero_llegada": numero_llegada,
            "tipo_evento": "messages.upsert",
            "mensaje": mensaje,
            "id_mensaje": id_mensaje,
            "id_mensaje_respondido": id_mensaje_respondido,
        }

        save_event(evento)
        logging.info(f"💾 Guardado evento: {evento}")

    except Exception as e:
        logging.error(f"Error procesando messages.upsert: {e}\nPayload: {json.dumps(payload, indent=2)}")

async def main():
    init_db()
    ws_url = f"{BASE_URL.replace('http', 'ws')}/ws/{INSTANCE}?apikey={API_KEY}"
    await sio.connect(ws_url, transports=["websocket"])
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
