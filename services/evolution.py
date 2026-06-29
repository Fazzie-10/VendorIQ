import httpx
from config import settings

BASE_URL = settings.EVOLUTION_API_URL
INSTANCE = settings.EVOLUTION_INSTANCE
HEADERS = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}


async def send_message(phone: str, text: str) -> dict:
    url = f"{BASE_URL}/message/sendText/{INSTANCE}"
    payload = {
        "number": phone,
        "text": text
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()


async def set_webhook(webhook_url: str) -> dict:
    url = f"{BASE_URL}/webhook/set/{INSTANCE}"
    payload = {
        "url": webhook_url,
        "webhook_by_events": False,
        "webhook_base64": False,
        "events": ["MESSAGES_UPSERT"]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        return response.json()
