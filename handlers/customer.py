from datetime import datetime, UTC
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


async def handle_add_debt(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")
    amount = entities.get("amount", 0)
    note = entities.get("note")

    if not customer_name or not amount:
        reply = "Try: 'Emeka owes me 45k' or 'Tunde collected goods worth 30k'"
        await send_message(phone, reply)
        return

    now = datetime.now(UTC)
    existing = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()

    if existing.data:
        customer = existing.data[0]
        old_balance = customer["balance"]
        new_balance = old_balance + amount
        supabase.table("customers").update({"balance": new_balance, "updated_at": now.isoformat()}).eq("id", customer["id"]).execute()
    else:
        old_balance = 0
        new_balance = amount
        supabase.table("customers").insert({
            "user_id": user["id"],
            "name": customer_name,
            "balance": new_balance,
            "updated_at": now.isoformat()
        }).execute()

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "debt",
        "amount": amount,
        "item": customer_name,
        "note": note,
        "created_at": now.isoformat()
    }).execute()

    reply = await generate_response("debt_added", {
        "customer": customer_name,
        "added_amount": amount,
        "total_owed": new_balance,
        "note": note
    })
    await send_message(phone, reply)


async def handle_record_payment(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")
    amount = entities.get("amount", 0)
    note = entities.get("note")

    if not customer_name or not amount:
        reply = "Try: 'Emeka paid 20k' or 'Tunde settled 10k'"
        await send_message(phone, reply)
        return

    existing = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()

    if not existing.data:
        reply = f"I don't have {customer_name} in your records. Check the spelling?"
        await send_message(phone, reply)
        return

    now = datetime.now(UTC)
    customer = existing.data[0]
    old_balance = customer["balance"]
    new_balance = max(0, old_balance - amount)
    supabase.table("customers").update({"balance": new_balance, "updated_at": now.isoformat()}).eq("id", customer["id"]).execute()

    supabase.table("transactions").insert({
        "user_id": user["id"],
        "type": "payment",
        "amount": amount,
        "item": customer_name,
        "note": note,
        "created_at": now.isoformat()
    }).execute()

    reply = await generate_response("payment_recorded", {
        "customer": customer_name,
        "paid": amount,
        "remaining_balance": new_balance,
        "note": note
    })
    await send_message(phone, reply)


async def handle_debt_query(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")
    now = datetime.now(UTC)

    if customer_name:
        result = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()
        if result.data:
            c = result.data[0]
            last_event = supabase.table("transactions").select("type,created_at").eq("user_id", user["id"]).eq("item", customer_name).order("created_at", desc=True).limit(1).execute()
            days_owed = None
            if last_event.data:
                days_owed = (now - datetime.fromisoformat(last_event.data[0]["created_at"].replace("Z", "+00:00"))).days

            reply = await generate_response("single_debt_query", {
                "customer": c["name"],
                "balance": c["balance"],
                "days_owed": days_owed
            })
        else:
            reply = f"No record for {customer_name}."
    else:
        result = supabase.table("customers").select("*").eq("user_id", user["id"]).gt("balance", 0).order("balance", desc=True).execute()
        debtors_data = []
        for c in result.data:
            last_event = supabase.table("transactions").select("type,created_at").eq("user_id", user["id"]).eq("item", c["name"]).order("created_at", desc=True).limit(1).execute()
            days_owed = None
            if last_event.data:
                days_owed = (now - datetime.fromisoformat(last_event.data[0]["created_at"].replace("Z", "+00:00"))).days
            debtors_data.append({"name": c["name"], "balance": c["balance"], "days_owed": days_owed})

        reply = await generate_response("all_debts_query", {
            "debtors": debtors_data,
            "total_outstanding": sum(c["balance"] for c in result.data)
        })

    await send_message(phone, reply)
