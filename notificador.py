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

    if msg.startswith("1") or msg.startswith("presente"):
        # Eliminar "1" o "presente" y guardar lo que sigue como aclaración
        aclaracion = msg.replace("presente", "", 1).replace("1", "", 1).strip()
        if aclaracion:
            texto = (
                f"🙌 Gracias {nombre}!\n"
                "Tu asistencia quedó registrada como ✅ PRESENTE.\n"
                f"Aclaración: {aclaracion}\n"
                "¡Que tengas un excelente día! 🌟"
            )
        else:
            texto = (
                f"🙌 Gracias {nombre}!\n"
                "Tu asistencia quedó registrada como ✅ PRESENTE.\n"
                "¡Que tengas un excelente día! 🌟"
            )
        send_text(numero, texto)

    elif msg.startswith("2") or msg.startswith("ausente") or msg.startswith("causa:"):
        aclaracion = msg.replace("ausente", "", 1).replace("2", "", 1).replace("causa:", "", 1).strip()
        if aclaracion:
            texto = (
                f"📌 Hola {nombre},\n"
                f"Registramos tu respuesta como ❌ AUSENTE.\n"
                f"Motivo: {aclaracion}\n"
                "Gracias por avisar 🙏, ¡esperamos verte pronto!"
            )
        else:
            texto = (
                f"📌 Hola {nombre},\n"
                "Registramos tu respuesta como ❌ AUSENTE.\n"
                "Gracias por avisar 🙏, ¡esperamos verte pronto!"
            )
        send_text(numero, texto)

    else:
        # Mensaje no válido → no responder
        return
