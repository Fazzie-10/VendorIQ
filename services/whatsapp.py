import httpx
from config import settings

GREEN_API_BASE = f"https://api.green-api.com/waInstance{settings.GREEN_API_INSTANCE_ID}"


async def send_message(phone: str, text: str) -> dict:
    url = f"{GREEN_API_BASE}/sendMessage/{settings.GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",
        "message": text
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def download_media(message_id: str) -> tuple[bytes, str]:
    """Download voice/audio media from Green API. Returns (bytes, mime_type)."""
    url = f"{GREEN_API_BASE}/downloadFile/{settings.GREEN_API_TOKEN}/{message_id}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "audio/ogg")
        return response.content, content_type


async def set_webhook(webhook_url: str) -> dict:
    url = f"{GREEN_API_BASE}/setSettings/{settings.GREEN_API_TOKEN}"
    payload = {
        "webhookUrl": webhook_url
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
