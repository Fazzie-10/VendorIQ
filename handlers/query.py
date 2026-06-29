from datetime import datetime, UTC, timedelta
from services.db import get_supabase
from services.evolution import send_message
from services.gemini import generate_response


async def handle_revenue_query(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    period = entities.get("period", "today")
    now = datetime.now(UTC)

    if period == "today" or not period:
        start = now.date().isoformat()
        label = "Today"
    elif period == "this week":
        start = (now - timedelta(days=now.weekday())).date().isoformat()
        label = "This week"
    elif period == "this month":
        start = now.replace(day=1).date().isoformat()
        label = "This month"
    elif period == "yesterday":
        start = (now - timedelta(days=1)).date().isoformat()
        label = "Yesterday"
    else:
        start = now.date().isoformat()
        label = "Today"

    sales = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "sale").gte("created_at", start).execute()
    expenses = supabase.table("transactions").select("amount").eq("user_id", user["id"]).eq("type", "expense").gte("created_at", start).execute()

    total_sales = sum(r["amount"] for r in sales.data)
    total_expenses = sum(r["amount"] for r in expenses.data)
    profit = total_sales - total_expenses

    reply = await generate_response("revenue_query", {
        "period": label,
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "profit": profit,
        "transaction_count": len(sales.data)
    })
    await send_message(phone, reply)
