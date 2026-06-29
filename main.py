from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from models.schemas import EvolutionWebhookPayload
from handlers.router import route_message
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


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

    # Normalize Nigerian numbers to international format
    if phone.startswith("0"):
        phone = "234" + phone[1:]
    elif phone.startswith("234"):
        pass  # already correct
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
        payload = EvolutionWebhookPayload(**raw)

        if payload.is_from_me or payload.is_group:
            return {"status": "ignored"}
        if payload.event != "messages.upsert":
            return {"status": "ignored"}
        if not payload.message_text:
            return {"status": "no_text"}

        await route_message(
            phone=payload.sender_phone,
            text=payload.message_text,
            push_name=payload.push_name
        )

    except Exception as e:
        print(f"Webhook error: {e}")

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "VendorIQ"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
