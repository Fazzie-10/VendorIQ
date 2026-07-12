import uuid
import httpx
from config import settings

GREEN_API_BASE = f"https://api.green-api.com/waInstance{settings.GREEN_API_INSTANCE_ID}"

_temp_files: dict[str, bytes] = {}


def store_temp_file(data: bytes) -> str:
    file_id = uuid.uuid4().hex[:16]
    _temp_files[file_id] = data
    return file_id


def get_temp_file(file_id: str) -> bytes | None:
    return _temp_files.pop(file_id, None)


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
    file_id = store_temp_file(file_bytes)
    base_url = settings.APP_PUBLIC_URL or "http://localhost:8000"
    file_url = f"{base_url}/temp/{file_id}/{filename}"
    url = f"{GREEN_API_BASE}/sendFileByUrl/{settings.GREEN_API_TOKEN}"
    payload = {
        "chatId": f"{phone}@c.us",
        "urlFile": file_url,
        "fileName": filename,
        "caption": caption,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception:
            return False


async def download_media(message_id: str) -> tuple[bytes, str]:
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
