import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.depencies import get_news_service
from app.schemas.news import NewsFilterParams, NewsListResponse, NewsResponse
from app.services.news import NewsService

router = APIRouter(prefix="/news", tags=["news"])


@router.get(
    "",
    response_model=NewsListResponse,
    summary="Список новостей с фильтрацией и полнотекстовым поиском",
)
async def list_news(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    search: str | None = Query(None, description="Полнотекстовый поиск"),
    source_domain: str | None = Query(
        None, description="Фильтрация по домену источника"
    ),
    category: str | None = Query(None, description="Фильтрация по категории"),
    tag: str | None = Query(None, description="Фильтрация по тегу"),
    status: str | None = Query(None, description="Фильтрация по статусу обработки"),
    author: str | None = Query(None, description="Фильтрация по автору"),
    published_from: str | None = Query(
        None, description="ISO datetime фильтрация по дате публикации с"
    ),
    published_to: str | None = Query(
        None, description="ISO datetime фильтрация по дате публикации до"
    ),
    service: NewsService = Depends(get_news_service),
) -> NewsListResponse:
    params = NewsFilterParams(
        page=page,
        size=size,
        search=search,
        source_domain=source_domain,
        category=category,
        tag=tag,
        status=status,
        author=author,
        published_from=published_from,
        published_to=published_to,
    )
    items, total = await service.list_with_filters(params)
    pages = math.ceil(total / size) if total else 0
    return NewsListResponse(
        items=[NewsResponse.model_validate(n) for n in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/{news_id}",
    response_model=NewsResponse,
    summary="Get a single news article with full enriched data",
)
async def get_news(
    news_id: uuid.UUID,
    service: NewsService = Depends(get_news_service),
) -> NewsResponse:
    try:
        news = await service.get_by_id(news_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return NewsResponse.model_validate(news)
