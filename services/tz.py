from datetime import datetime, timezone, timedelta

NIGERIA_TZ = timezone(timedelta(hours=1))


def now_nigeria() -> datetime:
    return datetime.now(NIGERIA_TZ)
