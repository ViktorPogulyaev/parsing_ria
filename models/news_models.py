import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import Index
from sqlalchemy.sql import func

from configuration.database import Base


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
 
    # enrichment: Mapped["NewsExtention | None"] = relationship(
    #     "NewsEnrichment", back_populates="news", uselist=False, lazy="selectin"
    # )
 
    __table_args__ = (
        Index("ix_news_source_domain", "source_domain"),
        Index("ix_news_published_at", "published_at"),
    )
 
    def __repr__(self) -> str:
        return f"<News id={self.id} title={self.title[:40]!r}>"


class NewsExtention(Base):
    """Расширенная информация по новостям"""

    __abstract__ = True