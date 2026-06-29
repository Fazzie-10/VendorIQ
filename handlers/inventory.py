from datetime import datetime, UTC
from services.db import get_supabase
from services.evolution import send_message
from services.gemini import generate_response


async def handle_update(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    item = entities.get("item")
    quantity = entities.get("quantity")

    if not item or not quantity:
        await send_message(phone, "Try: 'Received 50 bags of rice' or 'Stock: 20 cartons of indomie'")
        return

    existing = supabase.table("inventory").select("*").eq("user_id", user["id"]).ilike("item", item).execute()

    if existing.data:
        inv = existing.data[0]
        new_qty = inv["quantity"] + quantity
        supabase.table("inventory").update({
            "quantity": new_qty,
            "updated_at": datetime.now(UTC).isoformat()
        }).eq("id", inv["id"]).execute()
    else:
        new_qty = quantity
        supabase.table("inventory").insert({
            "user_id": user["id"],
            "item": item,
            "quantity": new_qty,
            "unit": entities.get("unit", "units")
        }).execute()

    reply = await generate_response("inventory_updated", {
        "item": item,
        "added": quantity,
        "total": new_qty
    })
    await send_message(phone, reply)
