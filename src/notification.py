import requests
from prefect import task

from src.config import settings


# Уведомление в Telegram
@task
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
    data = {"chat_id": settings.TG_CHAT_ID, "text": message}
    requests.post(url, data=data)
