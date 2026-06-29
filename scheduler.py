from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import settings
from services.db import get_supabase
from handlers.summary import send_daily_summary

scheduler = AsyncIOScheduler()


async def send_all_summaries():
    supabase = get_supabase()
    result = supabase.table("users").select("*").eq("status", "active").execute()
    for user in result.data:
        try:
            await send_daily_summary(user["phone"], user)
        except Exception as e:
            print(f"Summary failed for {user['phone']}: {e}")


def start_scheduler():
    scheduler.add_job(
        send_all_summaries,
        CronTrigger(hour=settings.DAILY_SUMMARY_HOUR, minute=settings.DAILY_SUMMARY_MINUTE),
        id="daily_summary",
        replace_existing=True
    )
    scheduler.start()
