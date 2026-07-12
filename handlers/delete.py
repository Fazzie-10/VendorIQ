from datetime import datetime, UTC
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


async def handle_delete(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    target_type = entities.get("target_type")
    amount = entities.get("amount", 0)
    customer_name = entities.get("customer_name")
    period = entities.get("period")
    user_id = user["id"]

    if customer_name and target_type == "debt" and period == "all":
        result = supabase.table("customers").select("*").eq("user_id", user_id).ilike("name", customer_name).execute()
        if not result.data:
            await send_message(phone, f"I don't see {customer_name} in your records.")
            return
        customer = result.data[0]
        old_balance = customer["balance"]
        supabase.table("customers").update({"balance": 0, "updated_at": datetime.now(UTC).isoformat()}).eq("id", customer["id"]).execute()
        reply = await generate_response("debt_deleted", {
            "customer": customer_name,
            "cleared_amount": old_balance
        })
        await send_message(phone, reply)
        return

    if customer_name and amount:
        result = supabase.table("transactions").select("*").eq("user_id", user_id).ilike("item", customer_name).eq("amount", amount).order("created_at", desc=True).limit(1).execute()
        if result.data:
            txn = result.data[0]
            supabase.table("transactions").delete().eq("id", txn["id"]).execute()
            reply = await generate_response("record_deleted", {
                "record_type": txn["type"],
                "amount": txn["amount"],
                "item": txn.get("item", ""),
                "customer": customer_name
            })
            await send_message(phone, reply)
            return

    if period == "last":
        if target_type:
            result = supabase.table("transactions").select("*").eq("user_id", user_id).eq("type", target_type).order("created_at", desc=True).limit(1).execute()
        else:
            result = supabase.table("transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()

        if result.data:
            txn = result.data[0]
            supabase.table("transactions").delete().eq("id", txn["id"]).execute()
            reply = await generate_response("record_deleted", {
                "record_type": txn["type"],
                "amount": txn["amount"],
                "item": txn.get("item", ""),
                "customer": txn.get("item", "")
            })
            await send_message(phone, reply)
            return

    await send_message(phone, "I couldn't find what you want to delete. Try: 'Delete my last sale' or 'Delete Emeka's debt'")
