from datetime import datetime, UTC
from services.db import get_supabase
from services.evolution import send_message
from services.gemini import generate_response


async def handle_log_sale(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    amount = entities.get("amount", 0)
    item = entities.get("item", "goods")
    quantity = entities.get("quantity")

    if not amount:
        await send_message(phone, "I couldn't read the amount. Try: 'Sold 3 bags of rice at 52k'")
        return

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "sale",
        "amount": amount,
        "item": item,
        "quantity": quantity,
        "created_at": datetime.now(UTC).isoformat()
    }).execute()

    today = datetime.now(UTC).date().isoformat()
    result = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "sale").gte("created_at", today).execute()
    today_total = sum(r["amount"] for r in result.data)

    reply = await generate_response("sale_logged", {
        "item": item,
        "quantity": quantity,
        "amount": amount,
        "today_total": today_total
    })
    await send_message(phone, reply)


async def handle_log_expense(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    amount = entities.get("amount", 0)
    item = entities.get("item", "expense")

    if not amount:
        await send_message(phone, "Couldn't read the amount. Try: 'Bought goods for 30k'")
        return

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "expense",
        "amount": amount,
        "item": item,
        "created_at": datetime.now(UTC).isoformat()
    }).execute()

    reply = await generate_response("expense_logged", {"item": item, "amount": amount})
    await send_message(phone, reply)
