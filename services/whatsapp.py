import httpx
from config import settings

GREEN_API_BASE = f"https://api.green-api.com/waInstance{settings.GREEN_API_INSTANCE_ID}"
GREEN_MEDIA_BASE = f"https://media.green-api.com/waInstance{settings.GREEN_API_INSTANCE_ID}"


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


async def send_file_upload(phone: str, file_bytes: bytes, filename: str, caption: str = "") -> bool:
    url = f"{GREEN_MEDIA_BASE}/sendFileByUpload/{settings.GREEN_API_TOKEN}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            files = {"file": (filename, file_bytes, "application/pdf")}
            data = {"chatId": f"{phone}@c.us", "fileName": filename, "caption": caption}
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            return True
        except Exception:
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


async def send_file_url(phone: str, file_bytes: bytes, filename: str, caption: str = "") -> bool:
    return await send_file_upload(phone, file_bytes, filename, caption)


async def set_webhook(webhook_url: str) -> dict:
    url = f"{GREEN_API_BASE}/setSettings/{settings.GREEN_API_TOKEN}"
    payload = {
        "webhookUrl": webhook_url
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
