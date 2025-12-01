# presentismo.py
import json
import os
import logging
from datetime import datetime, date, time
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from evolution_api import send_text
from db_logic import get_reporte
from reporte import formato_json

load_dotenv()

# Config desde .env
GRUPO_ID = os.getenv("GRUPO_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

COMPANEROS = {
    item.split(":")[0]: item.split(":")[1]
    for item in os.getenv("COMPANEROS", "").split(",")
}

NOMBRES_COMPLETOS = {
    "Guarnieri": "CT Franco Guarnieri",
    "Vera": "CT Víctor Adrián Vera",
    "Casals": "CT Mauricio Casals",
    "Olivera": "CT Ezequiel Waldo Olivera",
    "Amor": "CT Damián Gonzalo Amor",
    "Guaimas": "CT Fernando Darío Guaimás Rosado",
    "Perez": "CT Hernán Ariel Pérez",
    "Sanchez": "CT Santiago Sánchez Albornoz"
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
        if estado == "⚠️ AUSENTE SIN CAUSA":
            # Buscar el número a partir del nombre
            numero = next(num for num, nom in COMPANEROS.items() if nom == nombre)
            texto = (
                f"🌞 Buen día {nombre}!\n\n"
                "Todavía no registramos tu asistencia de hoy. Por favor, confirmá con una de estas opciones:\n\n"
                "1 para *PRESENTE* (Ej. 1, 1 estoy demorado...)\n"
                "2 para *AUSENTE* Seguido el motivo (Ej. 2 estoy enfermo, 2 bla bla..)\n\n"
                "Gracias por responder 💙"
            )
            send_text(numero, texto)

def enviar_reporte():
    """Genera reporte y lo manda al grupo y al admin."""
    inicio = _parse_time(FRANJA_INICIO)
    fin = _parse_time(FRANJA_FIN)

    reporte = get_reporte(COMPANEROS, fecha=date.today(), inicio=inicio, fin=fin)

    # # Para grupo (sin causas)
    # resumen = "\n".join([f"- {nombre}: {estado.split('(')[0].strip()}" for nombre, estado in reporte.items()])
    # send_text(GRUPO_ID, f"📊 Presentismo {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n{resumen}")

    # Generar JSON con formato oficial
    json_formateado = formato_json(reporte, NOMBRES_COMPLETOS)

    # Ruta del archivo en la raíz del proyecto
    ruta_archivo = os.path.join(os.getcwd(), "datos_parte.json")

    # Guardar archivo
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(json_formateado, f, indent=2, ensure_ascii=False)

    logging.info(f"📁 Archivo generado: {ruta_archivo}")

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
