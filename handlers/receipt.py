from services.gemini import generate_response
from services.whatsapp import send_file_url, send_message
from services.receipt import generate_receipt
from services.db import get_supabase


async def handle_receipt_request(phone: str, user: dict, entities: dict) -> None:
    supabase = get_supabase()
    lang = entities.get("_language", "english")
    user_id = user["id"]

    result = supabase.table("transactions").select("*").eq("user_id", user_id).eq("deleted", False).order("created_at", desc=True).limit(1).execute()

    if not result.data:
        await send_message(phone, "I don't have any transactions yet to generate a receipt for.")
        return

    txn = result.data[0]
    pdf_bytes = generate_receipt(
        business_name=user.get("business_name", "VendorIQ"),
        receipt_type=txn["type"],
        item=txn.get("item", "Goods"),
        amount=txn["amount"],
        quantity=txn.get("quantity"),
        customer=txn.get("item") if txn["type"] in ("debt", "payment") else None,
        note=txn.get("note"),
    )

    filename = f"receipt_{txn['type']}_{txn['id']}.pdf"
    success = await send_file_url(phone, pdf_bytes, filename, "Here's your receipt")

    if success:
        reply = await generate_response("receipt_sent", {
            "receipt_type": txn["type"],
            "amount": txn["amount"],
            "item": txn.get("item", "Goods"),
        }, language=lang)
        await send_message(phone, reply)
    else:
        await send_message(phone, "I generated the receipt but ran into an issue sending it. Please try again.")
