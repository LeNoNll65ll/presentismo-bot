# evolution_api.py
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
INSTANCE = os.getenv("INSTANCE")
API_KEY = os.getenv("API_KEY")

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def send_text(number: str, text: str):
    """Envia un mensaje de texto usando EvolutionAPI"""
    if not number.endswith("@s.whatsapp.net") and not number.endswith("@g.us"):
        number = f"{number}@s.whatsapp.net"

    url = f"{BASE_URL}/message/sendText/{INSTANCE}"
    payload = {"number": number, "text": text}

    try:
        r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        logging.info(f"📤 Enviado a {number}: {text} [{r.status_code}]")
        return r.json()
    except Exception as e:
        logging.error(f"❌ Error enviando mensaje a {number}: {e}")
        return None
