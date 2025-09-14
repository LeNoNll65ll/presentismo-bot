# presentismo.py
import os
import logging
from datetime import datetime, date, time
from apscheduler.schedulers.background import BackgroundScheduler
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


RECORDATORIOS = os.getenv("RECORDATORIOS", "07:00,07:15,07:30,08:00,08:15").split(",")
REPORTE_FINAL = os.getenv("REPORTE_FINAL", "08:30")
FRANJA_INICIO = os.getenv("FRANJA_INICIO", "06:00")
FRANJA_FIN = os.getenv("REPORTE_FINAL", "08:30")

logging.basicConfig(level=logging.INFO)

def _parse_time(s: str) -> time:
    h, m = map(int, s.split(":"))
    return time(h, m)

def enviar_recordatorio():
    """Manda recordatorio SOLO a los que no respondieron en la franja."""
    inicio = _parse_time(FRANJA_INICIO)
    fin = _parse_time(FRANJA_FIN)

    reporte = get_reporte(COMPANEROS, fecha=date.today(), inicio=inicio, fin=fin)

    for nombre, estado in reporte.items():
        if estado == "AUSENTE SIN CAUSA":
            # Buscar el número a partir del nombre
            numero = next(num for num, nom in COMPANEROS.items() if nom == nombre)
            texto = (
                f"Hola {nombre},\n"
                "Confirma tu presentismo:\n"
                "👉 Escribe *PRESENTE* si estás.\n"
                "👉 Escribe *AUSENTE: ...* indicando la causa si no estarás."
            )
            send_text(numero, texto)

def enviar_reporte():
    """Genera reporte y lo manda al grupo y al admin."""
    inicio = _parse_time(FRANJA_INICIO)
    fin = _parse_time(FRANJA_FIN)

    reporte = get_reporte(COMPANEROS, fecha=date.today(), inicio=inicio, fin=fin)

    # Para grupo (sin causas)
    resumen = "\n".join([f"- {nombre}: {estado.split('(')[0].strip()}" for nombre, estado in reporte.items()])
    send_text(GRUPO_ID, f"📊 Presentismo {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{resumen}")

    # Para admin (con causas)
    detalle = "\n".join([f"- {nombre}: {estado}" for nombre, estado in reporte.items()])
    send_text(ADMIN_ID, f"📋 Reporte detallado {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{detalle}")

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Recordatorios
    for t in RECORDATORIOS:
        try:
            h, m = map(int, t.split(":"))
            scheduler.add_job(enviar_recordatorio, "cron", hour=h, minute=m)
        except ValueError:
            logging.warning(f"⚠ Ignorando horario inválido en RECORDATORIOS: {t}")

    # Reporte final
    try:
        h, m = map(int, REPORTE_FINAL.split(":"))
        scheduler.add_job(enviar_reporte, "cron", hour=h, minute=m)
    except ValueError:
        logging.warning(f"⚠ Horario inválido en REPORTE_FINAL: {REPORTE_FINAL}")

    scheduler.start()
    logging.info("✅ Scheduler de presentismo iniciado")

    return scheduler 
