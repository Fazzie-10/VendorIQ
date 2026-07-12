from datetime import datetime, UTC
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


async def handle_summary(phone: str, user: dict, entities: dict) -> None:
    await send_daily_summary(phone, user)


async def send_daily_summary(phone: str, user: dict) -> None:
    supabase = get_supabase()
    today = datetime.now(UTC).date().isoformat()

    sales = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "sale").gte("created_at", today).execute()
    expenses = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "expense").gte("created_at", today).execute()
    debtors = supabase.table("customers").select("name,balance").eq("user_id", user["id"]).gt("balance", 0).order("balance", desc=True).limit(5).execute()
    low_stock = supabase.table("inventory").select("item,quantity,unit").eq("user_id", user["id"]).lt("quantity", 5).execute()

    total_sales = sum(r["amount"] for r in sales.data)
    total_expenses = sum(r["amount"] for r in expenses.data)

    reply = await generate_response(
        "daily_summary", {
            "business_name": user["business_name"],
            "date": today,
            "total_sales": total_sales,
            "total_expenses": total_expenses,
            "profit": total_sales - total_expenses,
            "top_debtors": [{"name": d["name"], "balance": d["balance"]} for d in debtors.data],
            "low_stock_items": [{"item": i["item"], "quantity": i["quantity"], "unit": i["unit"]} for i in low_stock.data]
        }
    )

    await send_message(phone, reply)
