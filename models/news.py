import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (DateTime, ForeignKey, Index, Integer, String, Text,
                        UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configuration.database import Base


class NewsEnrichmentStatus(StrEnum):
    """Статус обработки новости"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class News(Base):
    """Базовая информация по новостям — считается данной по условию задачи"""
 
    __tablename__ = "news"
 
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    source_domain: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    announcement: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
 
    enrichment: Mapped["NewsEnrichment | None"] = relationship(
        "NewsEnrichment", back_populates="news", uselist=False, lazy="selectin"
    )
 
    __table_args__ = (
        Index("ix_news_source_domain", "source_domain"),
        Index("ix_news_published_at", "published_at"),
    )
 
    def __repr__(self) -> str:
        return f"<News id={self.id} title={self.title[:40]!r}>"


class NewsEnrichment(Base):
    """Расширенная информация по новостям"""

    __tablename__ = "news_enrichment"
 
    news_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("news.id", ondelete="CASCADE"),
        primary_key=True,
    )
 
    # Cтатус обработки новости
    status: Mapped[str] = mapped_column(
        String(32), default=NewsEnrichmentStatus.PENDING, nullable=False
    )
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    parser_used: Mapped[str | None] = mapped_column(String(128))
 
    # Полный текст статьи
    full_text: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(512))
 
    # Основное изображение статьи
    main_image_url: Mapped[str | None] = mapped_column(String(2048))
    # Список изображений статьи [{url: str, caption: str | None, width: int | None, height: int | None}]
    images: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
 
    # Категории и теги статьи
    categories: Mapped[list[str]] = mapped_column(JSONB, default=list)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
 
    # Ключевые слова и краткое описание статьи
    keywords: Mapped[list[str]] = mapped_column(JSONB, default=list)
    summary: Mapped[str | None] = mapped_column(Text)
 
    # Количество просмотров и комментариев статьи
    views_count: Mapped[int | None] = mapped_column(Integer)
    comments_count: Mapped[int | None] = mapped_column(Integer)

    # Дополнительная информация о статье
    # {region: str, has_video: bool, language: str, reading_time_minutes: int, ...}
    article_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict
    )
 
    # Вектор полнотекстового поиска статьи
    search_vector: Mapped[Any] = mapped_column(TSVECTOR, nullable=True)
 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
 
    news: Mapped["News"] = relationship("News", back_populates="enrichment")
 
    __table_args__ = (
        Index("ix_enrichment_status", "status"),
        Index("ix_enrichment_search_vector", "search_vector", postgresql_using="gin"),
        UniqueConstraint("news_id", name="uq_enrichment_news_id"),
    )
 
    def __repr__(self) -> str:
        return f"<NewsEnrichment news_id={self.news_id} status={self.status}>"
