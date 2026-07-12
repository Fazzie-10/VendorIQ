import uuid
import logging
import httpx
from config import settings
from services.db import get_supabase

logger = logging.getLogger("vendoriq")

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


async def send_file_url(phone: str, file_bytes: bytes, filename: str, caption: str = "") -> bool:
    supabase = get_supabase()
    file_path = f"receipts/{uuid.uuid4().hex}_{filename}"

    try:
        supabase.storage.from_("receipts").upload(
            file_path,
            bytes(file_bytes),
            {"content-type": "application/pdf", "upsert": True}
        )
    except Exception as e:
        logger.error(f"Supabase storage upload failed: {e}")
        return False

    public_url = supabase.storage.from_("receipts").get_public_url(file_path)

    url = f"{GREEN_API_BASE}/sendFileByUrl/{settings.GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",
        "urlFile": public_url,
        "fileName": filename,
        "caption": caption,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Green API sendFileByUrl failed: {e}")
            return False


async def download_media(phone: str, message_id: str) -> tuple[bytes, str]:
    url = f"{GREEN_API_BASE}/downloadFile/{settings.GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",
        "idMessage": message_id,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        download_url = data.get("downloadUrl")
        if not download_url:
            raise ValueError("No downloadUrl in response")
        file_response = await client.get(download_url)
        file_response.raise_for_status()
        content_type = file_response.headers.get("content-type", "audio/ogg")
        return file_response.content, content_type


async def set_webhook(webhook_url: str) -> dict:
    url = f"{GREEN_API_BASE}/setSettings/{settings.GREEN_API_TOKEN}"
    payload = {
        "webhookUrl": webhook_url
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
