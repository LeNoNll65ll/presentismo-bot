# notificador.py
from evolution_api import send_text
import presentismo  # para COMPANEROS

def notificar_respuesta(numero: str, mensaje: str) -> None:
    """
    Revisa si la respuesta es válida y manda confirmación.
    - numero: teléfono del remitente
    - mensaje: texto crudo recibido
    """
    # Solo responder si está en la lista de compañeros
    if numero not in presentismo.COMPANEROS:
        return

    nombre = presentismo.COMPANEROS[numero]
    msg = mensaje.strip().lower()

    if msg.startswith("presente"):
        texto = f"✅ Hola {nombre}, tu presentismo fue registrado como PRESENTE."
        send_text(numero, texto)

    elif msg.startswith("ausente") or msg.startswith("causa:"):
        texto = f"❌ Hola {nombre}, tu presentismo fue registrado como AUSENTE ({mensaje})."
        send_text(numero, texto)

    else:
        # Mensaje no válido → no responder
        return
