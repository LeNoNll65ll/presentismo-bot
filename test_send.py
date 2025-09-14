# test_send.py
import logging
from evolution_api import send_text

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # Número de prueba (asegurate que esté en tu .env)
    numero = "5491170605689@s.whatsapp.net"
    texto = (
            f"Hola Gero,\n"
            "Confirma tu presentismo:\n"
            "👉 Escribe *PRESENTE* si estás.\n"
            "👉 Escribe *AUSENTE: ...* indicando la causa si no estarás."
        )
    resp = send_text(numero, texto)
    print("Respuesta:", resp)
