from celery import Celery

from app.configuration.config import settings

celery_app = Celery(
    "news_enrichment",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.broker.tasks"],
)

celery_app.conf.update(
    # Сериализация
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Поведение задач
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    # Маршрутизация
    task_default_queue="default",
    task_routes={
        "app.broker.tasks.enrich_news_task": {"queue": "enrichment"},
        "app.broker.tasks.enrich_batch_task": {"queue": "enrichment"},
        "app.broker.tasks.scan_pending_news_task": {"queue": "default"},
    },
    # Протухание результатов
    result_expires=86400,  # 24 часа
    # Расписание Beat — сканирование ожидающих новостей каждые N секунд
    beat_schedule={
        "scan-pending-news": {
            "task": "app.broker.tasks.scan_pending_news_task",
            "schedule": settings.enrichment_schedule_interval,
        },
    },
)
