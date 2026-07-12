from services.db import get_supabase
from services.whatsapp import send_message
from services.gemini import generate_response, generate_query_action, format_query_results
import hashlib
import time

_query_cache: dict[str, tuple[float, str]] = {}
CACHE_TTL = 300


def _cache_key(user_id: int, question: str) -> str:
    raw = f"{user_id}:{question.strip().lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(user_id: int, question: str) -> str | None:
    key = _cache_key(user_id, question)
    entry = _query_cache.get(key)
    if entry and (time.time() - entry[0]) < CACHE_TTL:
        return entry[1]
    if entry:
        del _query_cache[key]
    return None


def _set_cache(user_id: int, question: str, answer: str) -> None:
    key = _cache_key(user_id, question)
    _query_cache[key] = (time.time(), answer)
    if len(_query_cache) > 500:
        oldest = min(_query_cache.keys(), key=lambda k: _query_cache[k][0])
        del _query_cache[oldest]


async def handle_revenue_query(phone: str, user: dict, entities: dict) -> None:
    await handle_smart_query(phone, user, entities)


async def handle_smart_query(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    lang = entities.get("_language", "english")
    user_id = user["id"]
    original_text = entities.get("_original_text", "")

    cached = _get_cached(user_id, original_text)
    if cached:
        await send_message(phone, cached)
        return

    action = await generate_query_action(original_text, user.get("business_name", ""))

    table = action.get("table")
    if not table or action.get("error"):
        reply = await generate_response("unknown_query", {
            "question": original_text,
            "business_name": user.get("business_name", "Your business"),
        }, language=lang)
        await send_message(phone, reply)
        return

    type_filter = action.get("type_filter")
    start_date = action.get("start_date")
    end_date = action.get("end_date")
    aggregation = action.get("aggregation", "total")
    item_filter = action.get("item_filter")
    customer_filter = action.get("customer_filter")

    try:
        if table == "customers":
            query = supabase.table("customers").select("*").eq("user_id", user_id)
            if customer_filter:
                query = query.ilike("name", customer_filter)
            result = query.order("balance", desc=True).execute()
            data = _format_customer_data(result.data, aggregation)

        elif table == "inventory":
            query = supabase.table("inventory").select("*").eq("user_id", user_id)
            if item_filter:
                query = query.ilike("item", item_filter)
            result = query.order("quantity", asc=True).execute()
            data = _format_inventory_data(result.data, aggregation)

        else:
            query = supabase.table("transactions").select("*").eq("user_id", user_id)
            if type_filter and type_filter != "all":
                query = query.eq("type", type_filter)
            if start_date:
                query = query.gte("created_at", f"{start_date}T00:00:00")
            if end_date:
                query = query.lte("created_at", f"{end_date}T23:59:59")
            if item_filter:
                query = query.ilike("item", item_filter)

            if aggregation == "comparison":
                comp_start = action.get("comparison_start")
                comp_end = action.get("comparison_end")
                current_data = query.execute().data
                comp_query = supabase.table("transactions").select("*").eq("user_id", user_id)
                if type_filter and type_filter != "all":
                    comp_query = comp_query.eq("type", type_filter)
                if comp_start:
                    comp_query = comp_query.gte("created_at", f"{comp_start}T00:00:00")
                if comp_end:
                    comp_query = comp_query.lte("created_at", f"{comp_end}T23:59:59")
                comp_data = comp_query.execute().data
                data = _format_comparison_data(current_data, comp_data, start_date, end_date, comp_start, comp_end, aggregation)
            else:
                result = query.execute()
                data = _format_transaction_data(result.data, aggregation)

    except Exception as e:
        await send_message(phone, "Sorry, I ran into an error looking up that data. Try asking differently.")
        return

    reply = await format_query_results(original_text, data, language=lang)
    _set_cache(user_id, original_text, reply)
    await send_message(phone, reply)


def _format_transaction_data(rows: list, aggregation: str) -> dict:
    if not rows:
        return {"count": 0, "total": 0, "items": []}

    if aggregation == "total":
        return {
            "count": len(rows),
            "total": sum(r["amount"] for r in rows),
        }
    elif aggregation == "count":
        return {"count": len(rows)}
    elif aggregation == "daily":
        from collections import defaultdict
        by_day = defaultdict(list)
        for r in rows:
            day = r["created_at"][:10] if r.get("created_at") else "unknown"
            by_day[day].append(r)
        return {
            "daily": [
                {"date": day, "total": sum(r["amount"] for r in items), "count": len(items)}
                for day, items in sorted(by_day.items())
            ]
        }
    elif aggregation == "top":
        sorted_rows = sorted(rows, key=lambda r: r["amount"], reverse=True)[:5]
        return {
            "total": sum(r["amount"] for r in rows),
            "top": [
                {"item": r.get("item", ""), "amount": r["amount"], "date": r.get("created_at", "")[:10]}
                for r in sorted_rows
            ]
        }
    else:
        return {
            "count": len(rows),
            "total": sum(r["amount"] for r in rows),
            "items": [
                {"item": r.get("item", ""), "amount": r["amount"], "quantity": r.get("quantity"), "date": r.get("created_at", "")[:10]}
                for r in rows[:20]
            ]
        }


def _format_customer_data(rows: list, aggregation: str) -> dict:
    if not rows:
        return {"count": 0, "total_outstanding": 0, "debtors": []}

    return {
        "count": len(rows),
        "total_outstanding": sum(r["balance"] for r in rows),
        "debtors": [
            {"name": r["name"], "balance": r["balance"], "updated": r.get("updated_at", "")[:10]}
            for r in rows
        ]
    }


def _format_inventory_data(rows: list, aggregation: str) -> dict:
    if not rows:
        return {"count": 0, "items": []}

    return {
        "count": len(rows),
        "low_stock": [r for r in rows if r.get("quantity", 0) < 5],
        "items": [
            {"item": r["item"], "quantity": r["quantity"], "unit": r.get("unit", "units")}
            for r in rows
        ]
    }


def _format_comparison_data(current: list, comparison: list, cur_start, cur_end, comp_start, comp_end, aggregation: str) -> dict:
    cur_total = sum(r["amount"] for r in current)
    comp_total = sum(r["amount"] for r in comparison)
    change_pct = ((cur_total - comp_total) / comp_total * 100) if comp_total else 0

    return {
        "comparison": {
            "current_period": {"start": cur_start, "end": cur_end, "total": cur_total, "count": len(current)},
            "comparison_period": {"start": comp_start, "end": comp_end, "total": comp_total, "count": len(comparison)},
            "change_pct": round(change_pct, 1),
            "direction": "up" if change_pct > 0 else ("down" if change_pct < 0 else "same"),
        }
    }
