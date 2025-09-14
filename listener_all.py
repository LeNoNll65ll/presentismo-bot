import asyncio
import json
import logging
from datetime import datetime
import socketio
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
INSTANCE = os.getenv("INSTANCE")
API_KEY = os.getenv("API_KEY")

logging.basicConfig(level=logging.INFO)
sio = socketio.AsyncClient()

# ==== Handler genérico para cualquier evento ====
@sio.on("*")
async def catch_all(event, data=None):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data is None:
            payload = {"event": event}
        else:
            payload = {"event": event, "data": data}

        # Mostrar en consola
        logging.info(f"📡 [{ts}] Evento genérico:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

        # Guardar en archivo por día
        with open("all_events.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{ts}] {json.dumps(payload, ensure_ascii=False)}\n")

    except Exception as e:
        logging.error(f"Error procesando evento genérico {event}: {e}")

@sio.event
async def connect():
    logging.info("✅ Conectado al WebSocket de EvolutionAPI")

@sio.event
async def disconnect():
    logging.warning("❌ Desconectado del WebSocket")

async def main():
    await sio.connect(
        f"{BASE_URL}/{INSTANCE}",
        headers={"apikey": API_KEY},
        transports=["websocket"]
    )
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())
