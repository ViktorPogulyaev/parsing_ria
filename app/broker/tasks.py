import asyncio
import logging
import uuid

from celery import group

from app.configuration.config import settings
from app.configuration.database import AsyncSessionFactory
from app.core.exceptions import EnrichmentError, FetchError
from app.models.news import NewsEnrichmentStatus
from app.services.news import NewsService
from app.services.parsing_composer import EnrichmentComposer

from .celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Запуск async-кода из Celery: новый event loop на задачу + сброс пула БД."""
    from app.configuration.database import engine

    async def runner():
        try:
            return await coro
        finally:
            await engine.dispose()

    return asyncio.run(runner())


@celery_app.task(
    bind=True,
    name="app.broker.tasks.enrich_news_task",
    max_retries=settings.enrichment_max_retries,
    default_retry_delay=settings.enrichment_retry_delay,
    autoretry_for=(FetchError,),
    retry_backoff=True,
    retry_backoff_max=600,
    soft_time_limit=120,
    time_limit=180,
)
def enrich_news_task(self, news_id: str) -> dict:
    """Обогащение одной новости."""
    return _run_async(_enrich_single(self, uuid.UUID(news_id)))


async def _enrich_single(task, news_id: uuid.UUID) -> dict:

    async with AsyncSessionFactory() as session:
        service = NewsService(session)

        # Отметить что новость в процессе обогащения
        await service.update_enrichment(
            news_id,
            enriched_data={},
            status=NewsEnrichmentStatus.IN_PROGRESS,
        )
        await session.commit()

        try:
            news = await service.get_by_id(news_id)
            composer = EnrichmentComposer()
            enriched, parser_used = await composer.enrich(news)

            await service.update_enrichment(
                news_id,
                enriched_data=enriched.to_dict(),
                status=NewsEnrichmentStatus.DONE,
                parser_used=parser_used,
            )
            await session.commit()

            logger.info("Обогащена новость news_id=%s парсером=%s", news_id, parser_used)
            return {"news_id": str(news_id), "status": "done", "parser": parser_used}

        except EnrichmentError as exc:
            logger.error("Ошибка обогащения новости news_id=%s: %s", news_id, exc)
            await service.update_enrichment(
                news_id,
                enriched_data={},
                status=NewsEnrichmentStatus.FAILED,
                error_message=str(exc),
            )
            await session.commit()

            return {"news_id": str(news_id), "status": "failed", "error": str(exc)}

        except Exception as exc:
            logger.exception("Unexpected error enriching news_id=%s", news_id)
            await service.update_enrichment(
                news_id,
                enriched_data={},
                status=NewsEnrichmentStatus.FAILED,
                error_message=str(exc),
            )
            await session.commit()
            raise task.retry(exc=exc)


@celery_app.task(
    name="app.broker.tasks.enrich_batch_task",
    soft_time_limit=600,
    time_limit=700,
)
def enrich_batch_task(news_ids: list[str]) -> dict:
    """Обогащение списка новостей параллельно."""
    job = group(enrich_news_task.s(nid) for nid in news_ids)
    result = job.apply_async()
    logger.info("Отправлен обогащение для %d новостей", len(news_ids))
    return {"dispatched": len(news_ids), "group_id": result.id}


# @celery_app.task(name="app.broker.tasks.scan_pending_news_task")
# def scan_pending_news_task() -> dict:
#     """Периодическая задача: найти ожидающие новости и обогатить их."""
#     return _run_async(_scan_pending())


# async def _scan_pending() -> dict:
#     from app.core.database import AsyncSessionFactory
#     from app.services.news_service import NewsService

#     async with AsyncSessionFactory() as session:
#         service = NewsService(session)
#         pending = await service.get_pending_enrichment(
#             limit=settings.enrichment_batch_size
#         )

#     if not pending:
#         logger.debug("scan_pending: no pending news found")
#         return {"dispatched": 0}

#     news_ids = [str(n.id) for n in pending]
#     enrich_batch_task.delay(news_ids)
#     logger.info("scan_pending: dispatched %d items", len(news_ids))
#     return {"dispatched": len(news_ids)}