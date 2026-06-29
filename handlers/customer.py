from services.db import get_supabase
from services.evolution import send_message
from services.gemini import generate_response


async def handle_add_debt(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")
    amount = entities.get("amount", 0)

    if not customer_name or not amount:
        await send_message(phone, "Try: 'Emeka owes me 45k' or 'Tunde collected goods worth 30k'")
        return

    existing = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()

    if existing.data:
        customer = existing.data[0]
        new_balance = customer["balance"] + amount
        supabase.table("customers").update({"balance": new_balance}).eq("id", customer["id"]).execute()
    else:
        new_balance = amount
        supabase.table("customers").insert({
            "user_id": user["id"],
            "name": customer_name,
            "balance": new_balance
        }).execute()

    reply = await generate_response("debt_added", {
        "customer": customer_name,
        "added_amount": amount,
        "total_owed": new_balance
    })
    await send_message(phone, reply)


async def handle_record_payment(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")
    amount = entities.get("amount", 0)

    if not customer_name or not amount:
        await send_message(phone, "Try: 'Emeka paid 20k' or 'Tunde settled 10k'")
        return

    existing = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()

    if not existing.data:
        await send_message(phone, f"I don't have {customer_name} in your records. Check the spelling?")
        return

    customer = existing.data[0]
    new_balance = max(0, customer["balance"] - amount)
    supabase.table("customers").update({"balance": new_balance}).eq("id", customer["id"]).execute()

    reply = await generate_response("payment_recorded", {
        "customer": customer_name,
        "paid": amount,
        "remaining_balance": new_balance
    })
    await send_message(phone, reply)


async def handle_debt_query(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    customer_name = entities.get("customer_name")

    if customer_name:
        result = supabase.table("customers").select("*").eq("user_id", user["id"]).ilike("name", customer_name).execute()
        if result.data:
            c = result.data[0]
            reply = await generate_response("single_debt_query", {"customer": c["name"], "balance": c["balance"]})
        else:
            reply = f"No record for {customer_name}."
    else:
        result = supabase.table("customers").select("*").eq("user_id", user["id"]).gt("balance", 0).order("balance", desc=True).execute()
        reply = await generate_response("all_debts_query", {
            "debtors": [{"name": c["name"], "balance": c["balance"]} for c in result.data],
            "total_outstanding": sum(c["balance"] for c in result.data)
        })

    await send_message(phone, reply)
