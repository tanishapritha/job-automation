"""APScheduler configuration — filled in Phase 3."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the background scheduler (called from main.py lifespan)."""
    # Jobs will be registered in Phase 3
    scheduler.start()


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    scheduler.shutdown(wait=False)
