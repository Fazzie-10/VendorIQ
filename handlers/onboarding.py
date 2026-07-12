from services.whatsapp import send_message
from services.db import get_supabase


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
    message = (
        f"Hey {user['name']}! 👋 VendorIQ is ready.\n"
        f"Log a sale, check revenue, or type 'Summary' for your daily report."
    )
    await send_message(phone, message)


async def handle_unknown_intent(phone: str, user: dict, entities: dict) -> None:
    message = (
        "I didn't quite get that 🤔\n\n"
        "Try: 'Sold 5k', 'How much today?', 'Emeka owes 30k', or 'Summary'"
    )
    await send_message(phone, message)
