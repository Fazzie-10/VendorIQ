from datetime import datetime, timezone, timedelta

NIGERIA_TZ = timezone(timedelta(hours=1))


def now_nigeria() -> datetime:
    return datetime.now(NIGERIA_TZ)


def today_nigeria_start() -> str:
    """
    Returns Nigeria midnight as a full ISO timestamp string.
    Use this for Supabase .gte("created_at", ...) queries.
    
    A bare date string like "2026-07-12" is treated as UTC midnight by PostgreSQL.
    This causes records from early morning Nigeria time (which are still
    "yesterday" in UTC) to be excluded from "today" queries.
    
    This function returns "2026-07-12T00:00:00+01:00" — the correct timezone-aware
    Nigeria midnight — so PostgreSQL filters correctly.
    """
    now = now_nigeria()
    return now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
