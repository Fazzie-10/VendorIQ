from datetime import datetime, timedelta
from services.db import get_supabase

PENDING_TTL_MINUTES = 5


def store_pending(phone: str, intent: str, entities: dict, user: dict) -> None:
    supabase = get_supabase()
    now = datetime.utcnow()
    metadata = {
        "intent": intent,
        "entities": entities,
        "user_id": user["id"],
        "business_name": user.get("business_name", ""),
    }
    existing = supabase.table("conversation_sessions").select("id").eq("phone", phone).execute()
    if existing.data:
        supabase.table("conversation_sessions").update({
            "metadata": metadata,
            "last_activity": now.isoformat(),
            "expired_at": (now + timedelta(minutes=PENDING_TTL_MINUTES)).isoformat(),
        }).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("conversation_sessions").insert({
            "phone": phone,
            "session_id": f"pending_{phone}",
            "metadata": metadata,
            "last_activity": now.isoformat(),
            "expired_at": (now + timedelta(minutes=PENDING_TTL_MINUTES)).isoformat(),
        }).execute()


def get_pending(phone: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("conversation_sessions").select("metadata,last_activity").eq("phone", phone).order("last_activity", desc=True).limit(1).execute()
    if not result.data:
        return None
    row = result.data[0]
    meta = row.get("metadata")
    if not meta:
        return None
    last = datetime.fromisoformat(row["last_activity"].replace("Z", "+00:00"))
    if datetime.now(last.tzinfo) - last > timedelta(minutes=PENDING_TTL_MINUTES):
        clear_pending(phone)
        return None
    return meta


def clear_pending(phone: str) -> None:
    supabase = get_supabase()
    supabase.table("conversation_sessions").delete().eq("phone", phone).execute()
