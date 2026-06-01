import logging
import math
import uuid
from datetime import datetime

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.news import News, NewsEnrichment, NewsEnrichmentStatus
from app.schemas.news import NewsFilterParams

logger = logging.getLogger(__name__)
 
 
class NewsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
 
    async def get_by_id(self, news_id: uuid.UUID) -> News:
        """Получить новость по id"""
        stmt = (
            select(News)
            .options(selectinload(News.enrichment))
            .where(News.id == news_id)
        )
        result = await self.session.execute(stmt)
        news = result.scalar_one_or_none()
        if news is None:
            raise NotFoundError(f"Новость с id={news_id} не найдена")
        return news
 
 
    async def list_with_filters(
        self, params: NewsFilterParams
    ) -> tuple[list[News], int]:
        """Получить список новостей с фильтрацией"""
        stmt = select(News).options(selectinload(News.enrichment))
        count_stmt = select(func.count(News.id))
 
        stmt = stmt.outerjoin(News.enrichment)
        count_stmt = count_stmt.outerjoin(News.enrichment)
 
        # Полнотекстовый поиск
        if params.search:
            fts_query = func.plainto_tsquery("russian", params.search)
            fts_condition = NewsEnrichment.search_vector.op("@@")(fts_query)
            title_condition = News.title.ilike(f"%{params.search}%")
            stmt = stmt.where(or_(fts_condition, title_condition))
            count_stmt = count_stmt.where(or_(fts_condition, title_condition))
 
        # Filters
        if params.source_domain:
            stmt = stmt.where(News.source_domain == params.source_domain)
            count_stmt = count_stmt.where(News.source_domain == params.source_domain)
 
        if params.status:
            stmt = stmt.where(NewsEnrichment.status == params.status)
            count_stmt = count_stmt.where(NewsEnrichment.status == params.status)
 
        if params.published_from:
            stmt = stmt.where(News.published_at >= params.published_from)
            count_stmt = count_stmt.where(News.published_at >= params.published_from)
 
        if params.published_to:
            stmt = stmt.where(News.published_at <= params.published_to)
            count_stmt = count_stmt.where(News.published_at <= params.published_to)
 
        if params.category:
            stmt = stmt.where(
                NewsEnrichment.categories.contains([params.category])
            )
            count_stmt = count_stmt.where(
                NewsEnrichment.categories.contains([params.category])
            )
 
        if params.tag:
            stmt = stmt.where(NewsEnrichment.tags.contains([params.tag]))
            count_stmt = count_stmt.where(
                NewsEnrichment.tags.contains([params.tag])
            )
 
        if params.author:
            stmt = stmt.where(NewsEnrichment.author.ilike(f"%{params.author}%"))
            count_stmt = count_stmt.where(
                NewsEnrichment.author.ilike(f"%{params.author}%")
            )
 
        if params.has_video is not None:
            stmt = stmt.where(
                NewsEnrichment.metadata["has_video"].astext.cast(
                    type_=__import__("sqlalchemy").Boolean
                )
                == params.has_video
            )
 
        # Считаем общее количество новостей
        total = (await self.session.execute(count_stmt)).scalar_one()
 
        # Пагинация
        offset = (params.page - 1) * params.size
        stmt = stmt.order_by(News.published_at.desc()).offset(offset).limit(params.size)
 
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all()), total
 

    async def get_pending_enrichment(self, limit: int = 50) -> list[News]:
        """Получить список новостей с незавершенной обработкой"""
        stmt = (
            select(News)
            .join(News.enrichment)
            .where(NewsEnrichment.status == NewsEnrichmentStatus.PENDING)
            .order_by(News.published_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
 

    async def update_enrichment(
        self,
        news_id: uuid.UUID,
        enriched_data: dict,
        status: str,
        parser_used: str | None = None,
        error_message: str | None = None,
    ) -> NewsEnrichment:
        """Обновиление дополнительной информации о новости"""
        stmt = select(NewsEnrichment).where(NewsEnrichment.news_id == news_id)
        result = await self.session.execute(stmt)
        enrichment = result.scalar_one_or_none()
 
        if enrichment is None:
            enrichment = NewsEnrichment(news_id=news_id)
            self.session.add(enrichment)
 
        for key, value in enriched_data.items():
            if hasattr(enrichment, key):
                setattr(enrichment, key, value)
 
        enrichment.status = status
        enrichment.parser_used = parser_used
        enrichment.error_message = error_message
 
        if status == NewsEnrichmentStatus.DONE:
            enrichment.enriched_at = datetime.utcnow()
 
        await self.session.flush()
 
        # Обновление вектора полнотекстового поиска
        if status == NewsEnrichmentStatus.DONE and enriched_data.get("full_text"):
            await self.session.execute(
                text(
                    """
                    UPDATE news_enrichment SET search_vector =
                        setweight(to_tsvector('russian', coalesce(:title, '')), 'A') ||
                        setweight(to_tsvector('russian', coalesce(:full_text, '')), 'B') ||
                        setweight(to_tsvector('russian', coalesce(:summary, '')), 'C')
                    WHERE news_id = :news_id
                    """
                ),
                {
                    "news_id": str(news_id),
                    "title": enriched_data.get("title", ""),
                    "full_text": (enriched_data.get("full_text") or "")[:50000],
                    "summary": enriched_data.get("summary", ""),
                },
            )
 
        logger.info(
            "Обновлена дополнительная информация о новости id=%s статус=%s парсер=%s",
            news_id, status, parser_used,
        )
        return enrichment