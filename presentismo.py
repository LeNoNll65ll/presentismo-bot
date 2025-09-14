# presentismo.py
import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from evolution_api import send_text
from db_logic import get_reporte

load_dotenv()

# Config desde .env
GRUPO_ID = os.getenv("GRUPO_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

COMPANEROS = {
    item.split(":")[0]: item.split(":")[1]
    for item in os.getenv("COMPANEROS", "").split(",")
}

logging.basicConfig(level=logging.INFO)

def enviar_recordatorio():
    """Mensajes privados a cada compañero pidiendo confirmación."""
    for numero, nombre in COMPANEROS.items():
        texto = (
            f"Hola {nombre},\n"
            "Confirma tu presentismo:\n"
            "👉 Escribe *PRESENTE* si estás.\n"
            "👉 Escribe *AUSENTE: ...* indicando la causa si no estarás."
        )
        send_text(numero, texto)

def enviar_reporte():
    """Genera reporte y lo manda al grupo y al admin."""
    reporte = get_reporte(COMPANEROS)

    # Para grupo (sin causas)
    resumen = "\n".join([f"- {nombre}: {estado.split('(')[0].strip()}" for nombre, estado in reporte.items()])
    send_text(GRUPO_ID, f"📊 Presentismo {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{resumen}")

    # Para admin (con causas)
    detalle = "\n".join([f"- {nombre}: {estado}" for nombre, estado in reporte.items()])
    send_text(ADMIN_ID, f"📋 Reporte detallado {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{detalle}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Recordatorios
    for hora, minuto in [(7,0),(7,15),(7,30),(8,0),(8,15)]:
        scheduler.add_job(enviar_recordatorio, "cron", hour=hora, minute=minuto)

    # Reporte final
    scheduler.add_job(enviar_reporte, "cron", hour=8, minute=30)

    logging.info("✅ Bot de presentismo iniciado")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
