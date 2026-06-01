import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, Query

from schemas.news_enrichment import EnrichmentSchema


class NewsFilterParams(BaseModel):
    page: int = Query(1, ge=1, description="Номер страницы")
    size: int = Query(20, ge=1, le=100, description="Количество элементов на странице")
    search: str | None = Query(None, description="Полнотекстовый поиск")
    source_domain: str | None = Query(None, description="Фильтрация по домену источника")
    category: str | None = Query(None, description="Фильтрация по категории")
    tag: str | None = Query(None, description="Фильтрация по тегу")
    status: str | None = Query(None, description="Фильтрация по статусу обработки")
    author: str | None = Query(None, description="Фильтрация по автору")
    published_from: str | None = Query(None, description="ISO datetime фильтрация по дате публикации с")
    published_to: str | None = Query(None, description="ISO datetime фильтрация по дате публикации до")


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=1024)
    source_url: str = Field(..., max_length=2048)
    source_domain: str = Field(..., max_length=255)
    published_at: datetime
    announcement: str | None = None


class NewsResponse(NewsBase):
    model_config = ConfigDict(from_attributes=True)
 
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    enrichment: EnrichmentSchema | None = None

class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int
    page: int
    size: int
    pages: int

