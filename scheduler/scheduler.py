import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import logger
from services import collector_service

# Background scheduler for automated collection
def scheduled_collection():
    """Function to be called by scheduler"""
    if collector_service:
        try:
            asyncio.run(collector_service.collect_all_workflows())
            logger.info("Scheduled workflow collection completed")
        except Exception as e:
            logger.error(f"Scheduled collection failed: {e}")

def setup_scheduler():
    """Setup background scheduler for automated data collection"""
    scheduler = BackgroundScheduler()
    
    # Run daily at 2 AM
    scheduler.add_job(
        func=scheduled_collection,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_workflow_collection',
        name='Daily N8N Workflow Collection',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - daily collection at 2 AM")