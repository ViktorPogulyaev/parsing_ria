import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImageSchema(BaseModel):
    url: str
    caption: str | None = None
    width: int | None = None
    height: int | None = None


class EnrichSingleRequest(BaseModel):
    news_id: uuid.UUID


class EnrichBatchRequest(BaseModel):
    news_ids: list[uuid.UUID] = Field(..., min_length=1)


class EnrichTaskResponse(BaseModel):
    task_id: str
    news_id: uuid.UUID | None = None
    count: int | None = None
    message: str


class EnrichByCriteriaRequest(BaseModel):
    status: str | None = Field(None, description="Фильтрация по статусу обработки")
    source_domain: str | None = None
    limit: int = Field(50, ge=1, le=500)


class EnrichmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    status: str
    enriched_at: datetime | None = None
    parser_used: str | None = None
    error_message: str | None = None
 
    full_text: str | None = None
    author: str | None = None
    main_image_url: str | None = None
    images: list[ImageSchema] = Field(default_factory=list)
 
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    summary: str | None = None
 
    views_count: int | None = None
    comments_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
 