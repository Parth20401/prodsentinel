from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "prodsentinel_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.analysis"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,  # Process one task at a time
    broker_pool_limit=None,        # Disable pool to avoid broken pipes on free tier
    redis_backend_health_check_interval=30,
    broker_connection_retry_on_startup=True,
)
