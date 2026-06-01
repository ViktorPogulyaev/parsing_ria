import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.news_enrichment import EnrichmentSchema


class NewsFilterParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    search: str | None = None
    source_domain: str | None = None
    category: str | None = None
    tag: str | None = None
    status: str | None = None
    author: str | None = None
    published_from: str | None = None
    published_to: str | None = None


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
