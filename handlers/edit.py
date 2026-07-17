from services.tz import now_nigeria
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


async def handle_edit(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    user_id = user["id"]
    lang = entities.get("_language", "english")

    old_item = entities.get("old_item")
    new_item = entities.get("new_item")
    field = entities.get("field", "item")
    target_type = entities.get("target_type")
    period = entities.get("period")
    old_amount = entities.get("old_amount")
    new_amount = entities.get("new_amount")

    if field == "amount":
        if not new_amount:
            await send_message(phone, "What should the new amount be?")
            return
        old_val = old_amount
        new_val = new_amount
    else:
        if not new_item:
            await send_message(phone, "What should I change it to?")
            return
        old_val = old_item
        new_val = new_item

    txn = None

    if old_val:
        result = supabase.table("transactions").select("*").eq("user_id", user_id).eq("deleted", False)
        if target_type:
            result = result.eq("type", target_type)
        result = result.ilike("item", old_val).order("created_at", desc=True).limit(1).execute()
        if result.data:
            txn = result.data[0]
    elif period == "last":
        result = supabase.table("transactions").select("*").eq("user_id", user_id).eq("deleted", False)
        if target_type:
            result = result.eq("type", target_type)
        result = result.order("created_at", desc=True).limit(1).execute()
        if result.data:
            txn = result.data[0]

    if not txn:
        await send_message(phone, "I couldn't find the record to edit. Be more specific, e.g. 'change bo ti so to potato'")
        return

    update_data = {}
    if field == "item":
        update_data["item"] = new_item
    elif field == "amount":
        update_data["amount"] = new_amount
    elif field == "quantity":
        update_data["quantity"] = new_item
    update_data["updated_at"] = now_nigeria().isoformat()

    supabase.table("transactions").update(update_data).eq("id", txn["id"]).execute()

    reply = await generate_response("record_edited", {
        "old_item": txn.get("item", ""),
        "new_item": new_item,
        "old_amount": txn.get("amount"),
        "new_amount": new_amount,
        "field": field,
    }, language=lang)
    await send_message(phone, reply)
