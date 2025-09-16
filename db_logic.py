# db_logic.py
import sqlite3
from datetime import datetime, date, time

DB_FILE = "eventos.db"

def get_reporte(companeros: dict[str, str], 
                fecha: date | None = None,
                inicio: time | None = None,
                fin: time | None = None):
    """
    Genera reporte de presentismo desde la base SQLite.
    companeros -> dict {numero: nombre}
    - fecha: día a filtrar (por defecto hoy)
    - inicio, fin: ventana horaria (por defecto 06:00 - 08:30)
    Considera solo la PRIMERA respuesta de cada número.
    """
    if fecha is None:
        fecha = date.today()
    if inicio is None:
        inicio = time(6, 0)
    if fin is None:
        fin = time(8, 30)

    fecha_str = fecha.isoformat()
    inicio_str = inicio.strftime("%H:%M:%S")
    fin_str = fin.strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Traer todos los mensajes relevantes, ordenados por hora ascendente
    c.execute("""
        SELECT numero_salida, mensaje, fechahora
        FROM eventos
        WHERE DATE(fechahora) = ?
          AND TIME(fechahora) BETWEEN ? AND ?
          AND (
                mensaje LIKE 'presente%' COLLATE NOCASE
             OR mensaje LIKE 'ausente%' COLLATE NOCASE
             OR mensaje LIKE 'causa:%' COLLATE NOCASE
             OR mensaje LIKE '1%' COLLATE NOCASE
             OR mensaje LIKE '2%' COLLATE NOCASE
          )
        ORDER BY fechahora DESC
    """, (fecha_str, inicio_str, fin_str))
    vistos = {}  # numero -> (mensaje, fechahora)

    for numero, msg, ts in c.fetchall():
        if numero not in vistos:
            vistos[numero] = msg

    conn.close()

    # Construir reporte
    reporte = {}
    for numero, nombre in companeros.items():
        if numero in vistos:
            msg = vistos[numero].strip()
            msg_lower = msg.lower()

            if msg_lower.startswith("presente") or msg_lower.startswith("1"):
                # Sacar la palabra "presente"/"1" y mostrar lo que sigue
                resto = msg_lower.replace("presente", "", 1).replace("1", "", 1).strip()
                if resto:
                    reporte[nombre] = f"✅ PRESENTE ({resto})"
                else:
                    reporte[nombre] = "✅ PRESENTE"

            elif msg_lower.startswith("ausente") or msg_lower.startswith("2"):
                # Sacar "ausente"/"2"
                resto = msg_lower.replace("ausente", "", 1).replace("2", "", 1).strip()
                if resto:
                    reporte[nombre] = f"❌ AUSENTE CON CAUSA ({resto})"
                else:
                    reporte[nombre] = "❌ AUSENTE CON CAUSA"

            elif msg_lower.startswith("causa:"):
                # Sacar "causa:"
                resto = msg_lower.replace("causa:", "", 1).strip()
                if resto:
                    reporte[nombre] = f"❌ AUSENTE CON CAUSA ({resto})"
                else:
                    reporte[nombre] = "❌ AUSENTE CON CAUSA"
        else:
            reporte[nombre] = "⚠️ AUSENTE SIN CAUSA"

    return reporte
