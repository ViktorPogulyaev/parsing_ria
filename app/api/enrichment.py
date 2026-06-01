"""Enrichment trigger endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.depencies import get_news_service
from app.broker.tasks import enrich_batch_task, enrich_news_task
from app.core.exceptions import NotFoundError
from app.models.news import NewsEnrichmentStatus
from app.schemas.news_enrichment import (EnrichBatchRequest,
                                         EnrichByCriteriaRequest,
                                         EnrichSingleRequest, EnrichTaskResponse)
from app.services.news import NewsService

router = APIRouter(prefix="/enrich", tags=["enrichment"])


@router.post(
    "/single",
    response_model=EnrichTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Добавление в очередь обогащения одной новости",
)
async def enrich_single(
    payload: EnrichSingleRequest,
    service: NewsService = Depends(get_news_service),
) -> EnrichTaskResponse:
    # Проверяем что новость существует
    try:
        await service.get_by_id(payload.news_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    task = enrich_news_task.delay(str(payload.news_id))
    return EnrichTaskResponse(
        task_id=task.id,
        news_id=payload.news_id,
        message=f"Новости {payload.news_id} добавлена в очередь обогащения",
    )


@router.post(
    "/batch",
    response_model=EnrichTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Добавление в очередь обогащения нескольких новостей",
)
async def enrich_batch(
    payload: EnrichBatchRequest,
    service: NewsService = Depends(get_news_service),
) -> EnrichTaskResponse:
    news_ids = [str(nid) for nid in payload.news_ids]
    task = enrich_batch_task.delay(news_ids)
    return EnrichTaskResponse(
        task_id=task.id,
        count=len(news_ids),
        message=f"Обогащение новостей {len(news_ids)} добавлено в очередь",
    )


@router.post(
    "/by-criteria",
    response_model=EnrichTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Добавление в очередь обогащения по фильтру",
)
async def enrich_by_criteria(
    payload: EnrichByCriteriaRequest,
    service: NewsService = Depends(get_news_service),
) -> EnrichTaskResponse:
    from app.schemas.news import NewsFilterParams

    params = NewsFilterParams(
        size=payload.limit,
        status=payload.status or NewsEnrichmentStatus.PENDING,
        source_domain=payload.source_domain,
    )
    items, _ = await service.list_with_filters(params)

    if not items:
        return EnrichTaskResponse(
            task_id="",
            count=0,
            message="Нет новостей соответствующих критериям",
        )

    news_ids = [str(n.id) for n in items]
    task = enrich_batch_task.delay(news_ids)
    return EnrichTaskResponse(
        task_id=task.id,
        count=len(news_ids),
        message=f"Обогащение новостей {len(news_ids)} добавлено в очередь",
    )
