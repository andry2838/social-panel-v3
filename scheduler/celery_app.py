from celery import Celery
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
