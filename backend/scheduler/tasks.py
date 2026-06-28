"""
APScheduler background tasks.
Jobs are defined here and registered on app startup.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
_scheduler = BackgroundScheduler()


def start_scheduler():
    """Register all jobs and start the scheduler."""
    from services.expiry_service import check_all_users_expiry

    # Daily expiry check at 8 AM
    _scheduler.add_job(
        check_all_users_expiry,
        CronTrigger(hour=8, minute=0),
        id="expiry_check",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()
    logger.info("APScheduler started")


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
