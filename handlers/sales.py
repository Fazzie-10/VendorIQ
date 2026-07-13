from services.tz import now_nigeria, today_nigeria_start
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response
from handlers.customer import upsert_customer_purchase


def _lang(entities: dict) -> str:
    return entities.get("_language", "english")


async def handle_log_sale(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    now = now_nigeria()
    lang = _lang(entities)
    user_id = user["id"]
    customer_name = entities.get("customer_name")
    note = entities.get("note")

    items = entities.get("items")
    if items:
        created_items = []
        for entry in items:
            amount = entry.get("amount", 0)
            if not amount:
                continue
            item = entry.get("item", "goods")
            quantity = entry.get("quantity")
            supabase.table("transactions").insert({
                "user_id": user_id,
                "type": "sale",
                "amount": amount,
                "item": item,
                "quantity": quantity,
                "customer_name": customer_name,
                "note": note,
                "created_at": now.isoformat()
            }).execute()
            created_items.append({"item": item, "amount": amount, "quantity": quantity})
            if customer_name:
                upsert_customer_purchase(supabase, user_id, customer_name, amount, now)

        today_start = today_nigeria_start()
        result = supabase.table("transactions").select("amount").eq("user_id", user_id).eq("type", "sale").eq("deleted", False).gte("created_at", today_start).execute()
        today_total = sum(r["amount"] for r in result.data)

        reply = await generate_response("sale_logged", {
            "items": created_items,
            "today_total": today_total,
            "customer_name": customer_name,
            "note": note,
        }, language=lang)
        await send_message(phone, reply)
        return

    amount = entities.get("amount", 0)
    item = entities.get("item", "goods")
    quantity = entities.get("quantity")

    if not amount:
        await send_message(phone, "I couldn't read the amount. Try: 'Sold 3 bags of rice at 52k'")
        return

    supabase.table("transactions").insert({
        "user_id": user_id,
        "type": "sale",
        "amount": amount,
        "item": item,
        "quantity": quantity,
        "customer_name": customer_name,
        "note": note,
        "created_at": now.isoformat()
    }).execute()

    if customer_name:
        upsert_customer_purchase(supabase, user_id, customer_name, amount, now)

    today_start = today_nigeria_start()
    result = supabase.table("transactions").select("amount").eq("user_id", user_id).eq("type", "sale").eq("deleted", False).gte("created_at", today_start).execute()
    today_total = sum(r["amount"] for r in result.data)

    reply = await generate_response("sale_logged", {
        "item": item,
        "quantity": quantity,
        "amount": amount,
        "today_total": today_total,
        "customer_name": customer_name,
        "note": note,
    }, language=lang)
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
