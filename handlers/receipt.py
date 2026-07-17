from services.gemini import generate_response
from services.whatsapp import send_file_url, send_message
from services.receipt import generate_receipt, generate_combined_receipt
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
    created_at = txn["created_at"]

    batch = supabase.table("transactions").select("*").eq("user_id", user_id).eq("created_at", created_at).eq("deleted", False).order("id", asc=True).execute()

    if len(batch.data) > 1:
        pdf_bytes = generate_combined_receipt(
            business_name=user.get("business_name", "VendorIQ"),
            receipt_type=txn["type"],
            items=[{"item": r["item"], "amount": r["amount"], "quantity": r.get("quantity")} for r in batch.data],
            total=sum(r["amount"] for r in batch.data),
            customer=txn.get("customer_name") or (txn.get("item") if txn["type"] in ("debt", "payment") else None),
        )
        filename = f"receipt_{txn['type']}_{txn['id']}.pdf"
        success = await send_file_url(phone, pdf_bytes, filename, "Here's your combined receipt")

        if success:
            reply = await generate_response("receipt_sent", {
                "receipt_type": txn["type"],
                "amount": sum(r["amount"] for r in batch.data),
                "item": f"{len(batch.data)} items",
            }, language=lang)
            await send_message(phone, reply)
        else:
            await send_message(phone, "I generated the receipt but ran into an issue sending it. Please try again.")
        return

    pdf_bytes = generate_receipt(
        business_name=user.get("business_name", "VendorIQ"),
        receipt_type=txn["type"],
        item=txn.get("item", "Goods"),
        amount=txn["amount"],
        quantity=txn.get("quantity"),
        customer=txn.get("customer_name") or (txn.get("item") if txn["type"] in ("debt", "payment") else None),
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
