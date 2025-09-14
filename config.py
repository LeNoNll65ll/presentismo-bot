import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
INSTANCE = os.getenv("INSTANCE")
API_KEY = os.getenv("API_KEY")
GROUP_JID = os.getenv("GROUP_JID")
