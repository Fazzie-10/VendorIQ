from services.gemini import parse_intent
from services.db import get_supabase
from services.whatsapp import send_message
from services.pending import store_pending, get_pending, clear_pending
from handlers import onboarding, sales, query, customer, inventory, summary, delete, receipt

WRITE_INTENTS = {"log_sale", "log_expense", "add_debt", "record_payment", "update_inventory", "delete_record"}

HANDLERS = {
    "log_sale": sales.handle_log_sale,
    "log_expense": sales.handle_log_expense,
    "add_debt": customer.handle_add_debt,
    "record_payment": customer.handle_record_payment,
    "query_revenue": query.handle_smart_query,
    "query_debt": customer.handle_debt_query,
    "update_inventory": inventory.handle_update,
    "get_summary": summary.handle_summary,
    "delete_record": delete.handle_delete,
    "request_receipt": receipt.handle_receipt_request,
    "greeting": onboarding.handle_greeting,
    "acknowledgment": onboarding.handle_acknowledgment,
    "status_response": onboarding.handle_status_response,
    "help": onboarding.handle_help,
    "unknown": onboarding.handle_unknown_intent,
}


def _build_preview(intent: str, entities: dict) -> str:
    if intent == "log_sale":
        items = entities.get("items")
        if items:
            parts = []
            for e in items:
                q = f"{e.get('quantity', '')} " if e.get("quantity") else ""
                parts.append(f"{q}{e.get('item', 'goods')} at N{e['amount']:,}")
            items_str = ", ".join(parts)
        else:
            q = f"{entities.get('quantity', '')} " if entities.get("quantity") else ""
            items_str = f"{q}{entities.get('item', 'goods')} at N{entities['amount']:,}"
        base = f"Sale of {items_str}"
        if entities.get("customer_name"):
            base += f" to {entities['customer_name']}"
        if entities.get("note"):
            base += f" ({entities['note']})"
        return base
    elif intent == "log_expense":
        return f"Expense of N{entities['amount']:,} for {entities.get('item', 'goods')}"
    elif intent == "add_debt":
        return f"Debt of N{entities['amount']:,} from {entities['customer_name']}"
    elif intent == "record_payment":
        return f"Payment of N{entities['amount']:,} from {entities['customer_name']}"
    elif intent == "update_inventory":
        return f"Stock update: {entities.get('quantity')} {entities.get('item', 'goods')}"
    elif intent == "delete_record":
        return "Delete record"
    return "Save this?"


async def route_message(phone: str, text: str, push_name: str = "") -> None:
    supabase = get_supabase()

    result = supabase.table("users").select("*").eq("phone", phone).execute()
    user = result.data[0] if result.data else None

    if not user:
        await onboarding.handle_unknown(phone, push_name)
        return

    if user["status"] == "pending":
        if text.strip().upper() == "START":
            await onboarding.activate(phone, user)
        else:
            await send_message(phone, f"Hi {user['business_name']}! Send START to activate your VendorIQ account 🚀")
        return

    if text.strip().upper() == "START":
        await onboarding.handle_help(phone, user, {})
        return

    parsed = await parse_intent(text)
    intent = parsed.get("intent", "unknown")
    entities = parsed.get("entities", {})
    language = parsed.get("language", "english")

    entities["_language"] = language
    entities["_original_text"] = text

    if intent == "confirm":
        pending = get_pending(phone)
        if not pending:
            await send_message(phone, "Nothing to confirm.")
            return
        p_intent = pending["intent"]
        p_entities = pending["entities"]
        p_entities["_language"] = entities.get("_language", "english")
        p_entities["_original_text"] = entities.get("_original_text", "")
        handler = HANDLERS.get(p_intent)
        if handler:
            await handler(phone=phone, user={"id": pending["user_id"], "business_name": pending.get("business_name", "")}, entities=p_entities)
        clear_pending(phone)
        return

    if intent == "reject":
        clear_pending(phone)
        await send_message(phone, "Cancelled.")
        return

    if intent in WRITE_INTENTS:
        preview = _build_preview(intent, entities)
        store_pending(phone, intent, entities, user)
        await send_message(phone, f"{preview}\n\nSave this? (yes/no)")
        return

    handler = HANDLERS.get(intent, onboarding.handle_unknown_intent)
    await handler(phone=phone, user=user, entities=entities)
