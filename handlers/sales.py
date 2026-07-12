from services.tz import now_nigeria, today_nigeria_start
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


def _lang(entities: dict) -> str:
    return entities.get("_language", "english")


async def handle_log_sale(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    amount = entities.get("amount", 0)
    item = entities.get("item", "goods")
    quantity = entities.get("quantity")
    note = entities.get("note")

    if not amount:
        await send_message(phone, "I couldn't read the amount. Try: 'Sold 3 bags of rice at 52k'")
        return

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "sale",
        "amount": amount,
        "item": item,
        "quantity": quantity,
        "note": note,
        "created_at": now_nigeria().isoformat()
    }).execute()

    today_start = today_nigeria_start()
    result = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "sale").gte("created_at", today_start).execute()
    today_total = sum(r["amount"] for r in result.data)

    reply = await generate_response("sale_logged", {
        "item": item,
        "quantity": quantity,
        "amount": amount,
        "today_total": today_total,
        "note": note
    }, language=_lang(entities))
    await send_message(phone, reply)


async def handle_log_expense(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    amount = entities.get("amount", 0)
    item = entities.get("item", "expense")
    note = entities.get("note")

    if not amount:
        await send_message(phone, "Couldn't read the amount. Try: 'Bought goods for 30k'")
        return

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "expense",
        "amount": amount,
        "item": item,
        "note": note,
        "created_at": now_nigeria().isoformat()
    }).execute()

    reply = await generate_response("expense_logged", {"item": item, "amount": amount, "note": note}, language=_lang(entities))
    await send_message(phone, reply)
