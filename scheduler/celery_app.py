from celery import Celery
from celery.schedules import crontab
import os

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery("social_panel", broker=redis_url)
app.conf.update(
    timezone="Europe/Paris",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_time_limit=3600,
    worker_max_tasks_per_child=50,
)

import scheduler.tasks  # noqa: enregistre les tâches

# Configuration d'un Beat Schedule statique, propre et robuste.
app.conf.beat_schedule = {
    "reset_daily_limits_at_midnight": {
        "task": "scheduler.tasks.reset_daily_limits",
        "schedule": crontab(hour=0, minute=0),
    },
    "run_active_accounts_daily_routines": {
        "task": "scheduler.tasks.dispatch_daily_routines",
        "schedule": crontab(minute="*/15"), # Toutes les 15 minutes
    }
}
