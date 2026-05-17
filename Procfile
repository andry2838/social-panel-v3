web: python api/main.py
worker: celery -A scheduler.celery_app worker -l info --concurrency=2
beat: celery -A scheduler.celery_app beat -l info
