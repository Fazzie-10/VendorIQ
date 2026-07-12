from services.gemini import parse_intent
from services.db import get_supabase
from services.whatsapp import send_message
from handlers import onboarding, sales, query, customer, inventory, summary, delete


async def route_message(phone: str, text: str, push_name: str = "") -> None:
    supabase = get_supabase()

    result = supabase.table("users").select("*").eq("phone", phone).execute()
    user = result.data[0] if result.data else None

    if not user:
        await onboarding.handle_unknown(phone, push_name)
        return

    if user["status"] == "pending":
        if text.strip().upper() == "START":
            await onboarding.activate(phone, user)
        else:
            await send_message(phone, f"Hi {user['name']}! Send START to activate your VendorIQ account 🚀")
        return

    parsed = await parse_intent(text)
    intent = parsed.get("intent", "unknown")
    entities = parsed.get("entities", {})

    handlers = {
        "log_sale": sales.handle_log_sale,
        "log_expense": sales.handle_log_expense,
        "add_debt": customer.handle_add_debt,
        "record_payment": customer.handle_record_payment,
        "query_revenue": query.handle_revenue_query,
        "query_debt": customer.handle_debt_query,
        "update_inventory": inventory.handle_update,
        "get_summary": summary.handle_summary,
        "delete_record": delete.handle_delete,
        "greeting": onboarding.handle_greeting,
        "unknown": onboarding.handle_unknown_intent,
    }

    handler = handlers.get(intent, onboarding.handle_unknown_intent)
    await handler(phone=phone, user=user, entities=entities)
