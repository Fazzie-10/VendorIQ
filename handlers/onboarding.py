from services.whatsapp import send_message
from services.db import get_supabase
from services.gemini import generate_response


WELCOME_MESSAGE = """Welcome to VendorIQ! 🎉

I'm your pocket business assistant. Here's what I can do:

📦 Log sales: "Sold 3 bags rice at 52k"
💰 Check revenue: "How much today?"
👤 Track debts: "Emeka owes 45k"
✅ Record payment: "Emeka paid 20k"
📊 Daily report: "Summary"

Try sending your first sale now!"""


async def activate(phone: str, user: dict) -> None:
    supabase = get_supabase()
    supabase.table("users").update({"status": "active"}).eq("phone", phone).execute()
    await send_message(phone, f"Account activated! {WELCOME_MESSAGE}")


async def handle_unknown(phone: str, push_name: str = "") -> None:
    name = push_name or "there"
    message = (
        f"Hi {name}! 👋 You don't have a VendorIQ account yet.\n\n"
        f"Sign up at vendoriq.app then send START here to get started."
    )
    await send_message(phone, message)


async def handle_greeting(phone: str, user: dict, entities: dict) -> None:
    lang = entities.get("_language", "english")
    reply = await generate_response("greeting", {
        "user_name": user["name"],
    }, language=lang)
    await send_message(phone, reply)


async def handle_help(phone: str, user: dict, entities: dict) -> None:
    # Hardcoded — never ask Gemini to list features, it invents things
    reply = f"""VendorIQ commands for {user['name']}:

Log sales: "Sold 3 bags rice at 52k"
Log expense: "Bought goods for 30k"
Check revenue: "How much today?" or "This week?"
Track debt: "Emeka owes 45k"
Record payment: "Emeka paid 20k"
Who owes me: "Who owes me?" or "Emeka balance"
Stock update: "Received 50 bags of rice"
Get summary: "Summary"
Delete record: "Delete my last sale"
Get receipt: "Send me a receipt"

Ask anything about your business in plain English."""
    await send_message(phone, reply)


async def handle_unknown_intent(phone: str, user: dict, entities: dict) -> None:
    lang = entities.get("_language", "english")
    reply = await generate_response("unknown", {
        "user_name": user["name"],
    }, language=lang)
    await send_message(phone, reply)
