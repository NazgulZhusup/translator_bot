import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = "https://translator-bot-kxxv.onrender.com/webhook"

def set_webhook():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
    params = {
        "url": WEBHOOK_URL
    }
    response = requests.get(url, params=params)
    print(response.json())

if __name__ == "__main__":
    set_webhook()