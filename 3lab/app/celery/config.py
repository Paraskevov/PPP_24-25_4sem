from celery import Celery
from app.core.config import settings

def create_celery_app():
    celery_app = Celery(
        "app",
        broker=settings.redis_url,
        backend=settings.redis_url
    )

    celery_app.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        result_expires=3600,
    )
    
    return celery_app

celery_app = create_celery_app()