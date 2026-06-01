from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.database import get_db_session
from app.services.news import NewsService


async def get_news_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[NewsService, None]:
    yield NewsService(session)
 