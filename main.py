import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vendoriq")

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from models.schemas import GreenAPIWebhookPayload
from handlers.router import route_message
from services.whatsapp import download_media, get_temp_file, send_message
from services.gemini import transcribe_audio
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting VendorIQ...")
    start_scheduler()
    logger.info(f"Scheduler started (daily summary at {settings.DAILY_SUMMARY_HOUR}:{settings.DAILY_SUMMARY_MINUTE:02d})")
    yield
    logger.info("VendorIQ shutdown complete")


app = FastAPI(title="VendorIQ", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"vendoriq_phone": settings.VENDORIQ_PHONE}
    )


@app.post("/register")
async def register(request: Request):
    data = await request.json()
    phone = data.get("phone", "").replace("+", "").replace(" ", "").replace("-", "")

    if phone.startswith("0"):
        phone = "234" + phone[1:]
    elif phone.startswith("234"):
        pass
    else:
        phone = "234" + phone
    name = data.get("name", "").strip()
    business_name = data.get("business_name", "").strip()

    if not all([phone, name, business_name]):
        raise HTTPException(status_code=400, detail="All fields required")

    from services.db import get_supabase
    supabase = get_supabase()

    supabase.table("users").upsert({
        "phone": phone,
        "name": name,
        "business_name": business_name,
        "status": "pending"
    }, on_conflict="phone").execute()

    return {"success": True, "message": f"Account created. Send START to {settings.VENDORIQ_PHONE}"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        raw = await request.json()
        payload = GreenAPIWebhookPayload(**raw)

        if payload.is_from_me or payload.is_group:
            logger.info(f"Ignored (from_me={payload.is_from_me}, group={payload.is_group})")
            return {"status": "ignored"}
        if payload.typeWebhook not in ("incomingMessageReceived",):
            logger.info(f"Ignored type: {payload.typeWebhook}")
            return {"status": "ignored"}

        if not payload.is_incoming_message:
            logger.info(f"Ignored type: {payload.typeWebhook}")
            return {"status": "ignored"}
        if payload.is_group:
            logger.info(f"Ignored group message")
            return {"status": "ignored"}

        if payload.is_audio and payload.audio_message_id:
            try:
                audio_bytes, mime_type = await download_media(payload.audio_message_id)
                transcribed = await transcribe_audio(audio_bytes, mime_type)
                if transcribed:
                    await route_message(
                        phone=payload.sender_phone,
                        text=transcribed,
                        push_name=payload.push_name
                    )
            except Exception as audio_err:
                logger.error(f"Voice note error: {audio_err}")
                await send_message(
                    payload.sender_phone,
                    "Sorry, I couldn't process that voice note. Please type your message instead."
                )
            return {"status": "ok"}

        if not payload.message_text:
            logger.info("Ignored empty non-voice message")
            return {"status": "no_text"}

        logger.info(f"Processing text from {payload.sender_phone}: {payload.message_text[:100]}")

        await route_message(
            phone=payload.sender_phone,
            text=payload.message_text,
            push_name=payload.push_name
        )

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)

    return {"status": "ok"}


@app.get("/temp/{file_id}/{filename:path}")
async def serve_temp_file(file_id: str, filename: str):
    data = get_temp_file(file_id)
    if data is None:
        raise HTTPException(status_code=404, detail="File not found or expired")
    from fastapi.responses import Response
    return Response(content=data, media_type="application/pdf")


@app.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "service": "VendorIQ"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
