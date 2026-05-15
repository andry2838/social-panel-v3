web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
worker: celery -A scheduler.celery_app worker -l info --concurrency=2
beat: celery -A scheduler.celery_app beat -l info
dashboard: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0
