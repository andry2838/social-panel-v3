web: sh -c 'uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}'
worker: celery -A scheduler.celery_app worker -l info --concurrency=2
beat: celery -A scheduler.celery_app beat -l info
