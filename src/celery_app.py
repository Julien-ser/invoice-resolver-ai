"""
Celery application configuration for background tasks.

This module sets up Celery with Redis broker and configures periodic tasks
for invoice status synchronization and other background operations.
"""

import os
from celery import Celery
from celery.schedules import crontab
from .core.config import settings

# Create Celery app
celery_app = Celery(
    "invoice_resolver",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["tasks.sync", "tasks.backup"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_times_limit=30 * 60,  # 30 minutes
    worker_max_tasks_per_child=1000,
    beat_schedule={
        "sync-invoice-status-every-15-minutes": {
            "task": "tasks.sync.sync_invoice_status",
            "schedule": crontab(minute="*/15"),
        },
        "backup-database-daily": {
            "task": "tasks.backup.run_backup",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM UTC
        },
    },
    beat_schedule_filename="celerybeat-schedule",
)

# Auto-discover tasks in the tasks module
celery_app.autodiscover_tasks(["tasks", "tasks.email"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to print request info."""
    print(f"Request: {self.request!r}")
