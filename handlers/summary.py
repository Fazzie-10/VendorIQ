from services.tz import now_nigeria, today_nigeria_start
from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response


async def handle_summary(phone: str, user: dict, entities: dict) -> None:
    lang = entities.get("_language", "english")
    await send_daily_summary(phone, user, lang)


async def send_daily_summary(phone: str, user: dict, language: str = "english") -> None:
    supabase = get_supabase()
    today_start = today_nigeria_start()

    sales = supabase.table("transactions").select("amount,item,quantity,note,created_at").eq("user_id", user["id"]).eq("type", "sale").gte("created_at", today_start).order("created_at", desc=True).execute()
    expenses = supabase.table("transactions").select("amount,item,quantity,note,created_at").eq("user_id", user["id"]).eq("type", "expense").gte("created_at", today_start).order("created_at", desc=True).execute()
    debtors = supabase.table("customers").select("name,balance,updated_at").eq("user_id", user["id"]).gt("balance", 0).order("balance", desc=True).limit(5).execute()
    low_stock = supabase.table("inventory").select("item,quantity,unit").eq("user_id", user["id"]).lt("quantity", 5).execute()

    total_sales = sum(r["amount"] for r in sales.data)
    total_expenses = sum(r["amount"] for r in expenses.data)

    reply = await generate_response(
        "daily_summary", {
            "business_name": user["business_name"],
            "date": now_nigeria().strftime("%A, %B %d, %Y"),
            "total_sales": total_sales,
            "total_expenses": total_expenses,
            "profit": total_sales - total_expenses,
            "today_sales": [{"item": s["item"], "amount": s["amount"], "quantity": s.get("quantity"), "note": s.get("note")} for s in sales.data],
            "today_expenses": [{"item": e["item"], "amount": e["amount"], "note": e.get("note")} for e in expenses.data],
            "top_debtors": [{"name": d["name"], "balance": d["balance"]} for d in debtors.data],
            "low_stock_items": [{"item": i["item"], "quantity": i["quantity"], "unit": i["unit"]} for i in low_stock.data]
        }, language=language
    )

    await send_message(phone, reply)
