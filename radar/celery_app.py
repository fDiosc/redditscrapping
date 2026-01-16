"""
Celery configuration for async task processing.
Requires Redis to be running and REDIS_URL environment variable to be set.
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis URL from environment or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "radar",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["radar.tasks.sync_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minute timeout
    task_soft_time_limit=540,  # 9 minute soft timeout
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_acks_late=True,  # Acknowledge after completion
)

# Optional: beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Example: 'cleanup-old-data': {
    #     'task': 'radar.tasks.maintenance.cleanup_old_data',
    #     'schedule': crontab(hour=3, minute=0),  # Run at 3 AM
    # },
}
