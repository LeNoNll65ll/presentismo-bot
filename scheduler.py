# scheduler.py
import datetime
import httpx
import logging
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BASE_URL, INSTANCE, API_KEY, GROUP_JID
from listener import POLL_FILE, CAUSAS_FILE

# Lista de compañeros
COMPANEROS = [
    "Guarnieri", "Vera", "Casals", "Olivera",
    "Amor", "Guaimas", "Perez", "Sanchez"
]

# Cliente HTTP global (se cierra en main.on_shutdown)
client = httpx.AsyncClient(timeout=10.0)

# Scheduler asíncrono (usa el event loop de FastAPI/Uvicorn)
scheduler = AsyncIOScheduler(timezone="America/Argentina/Buenos_Aires")

# -------------------------------
# Enviar poll al grupo (async)
# -------------------------------
async def send_poll():
    url = f"{BASE_URL}/message/sendPoll/{INSTANCE}"
    payload = {
        "number": GROUP_JID,
        "name": f"Presentismo {datetime.date.today().strftime('%d/%m/%Y')}",
        "selectableCount": 1,
        "values": COMPANEROS
    }
    headers = {"apikey": API_KEY}

    try:
        r = await client.post(url, json=payload, headers=headers)
        logging.info(f"Poll enviado: {r.status_code} {r.text}")
    except Exception as e:
        logging.error(f"Error enviando poll: {e}")

# -------------------------------
# Generar reporte a las 08:30
# -------------------------------
def generar_reporte():
    presentes, ausentes_causa, reporte = set(), set(), {}

    # 1) Leer presentes del archivo
    try:
        with open(POLL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            presentes = set(data.keys())
    except FileNotFoundError:
        presentes = set()

    # 2) Leer ausentes con causa (mensajes privados)
    try:
        with open(CAUSAS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            ausentes_causa = set(data.keys())
    except FileNotFoundError:
        ausentes_causa = set()

    # 3) Armar estados
    for nombre in COMPANEROS:
        if nombre in presentes:
            reporte[nombre] = "PRESENTE"
        elif nombre in ausentes_causa:
            reporte[nombre] = "AUSENTE CON CAUSA"
        else:
            reporte[nombre] = "AUSENTE SIN CAUSA"

    logging.info("📊 Reporte final:\n" + json.dumps(reporte, indent=2, ensure_ascii=False))

    with open("reporte.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)

# -------------------------------
# Inicializar scheduler
# -------------------------------
def start_scheduler():
    # Ajustá estos horarios a producción:
    # - Poll diario 07:00
    # - Reporte 08:30
    scheduler.add_job(send_poll, "cron", hour=7, minute=0)
    scheduler.add_job(generar_reporte, "cron", hour=8, minute=30)

    # Para pruebas rápidas, descomentá y poné hora/minuto actual+1
    # scheduler.add_job(send_poll, "cron", hour=22, minute=42)
    # scheduler.add_job(generar_reporte, "cron", hour=22, minute=45)

    scheduler.start()
    logging.info("✅ Scheduler iniciado (poll a las 07:00, reporte a las 08:30)")
