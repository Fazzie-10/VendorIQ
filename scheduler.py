import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import settings
from services.db import get_supabase
from handlers.summary import send_daily_summary

logger = logging.getLogger("vendoriq.scheduler")
scheduler = AsyncIOScheduler()


async def send_all_summaries():
    supabase = get_supabase()
    logger.info("Starting daily summaries for all active users")
    result = supabase.table("users").select("*").eq("status", "active").execute()
    active_count = len(result.data)
    logger.info(f"Found {active_count} active users")

    for user in result.data:
        try:
            await send_daily_summary(user["phone"], user)
            logger.info(f"Summary sent to {user['phone']}")
        except Exception as e:
            logger.error(f"Summary failed for {user['phone']}: {e}")

    logger.info("Daily summaries complete")


def start_scheduler():
    scheduler.add_job(
        send_all_summaries,
        CronTrigger(hour=settings.DAILY_SUMMARY_HOUR, minute=settings.DAILY_SUMMARY_MINUTE),
        id="daily_summary",
        replace_existing=True
    )
    scheduler.start()
