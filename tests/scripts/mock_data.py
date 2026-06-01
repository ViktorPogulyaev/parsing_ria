import asyncio
import sys
from pathlib import Path

# Добавляем путь к корневому каталогу проекта для корректного запуска скрипта
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.configuration.database import AsyncSessionFactory
from app.models.news import News, NewsEnrichment

SAMPLE_NEWS = [
    {
        "title": "Названа предварительная причина смерти пропавших в Омске сапбордистов",
        "source_url": "https://ria.ru/20260601/prichina-2096049115.html",
        "source_domain": "ria.ru",
        "published_at": datetime.utcnow() - timedelta(hours=2),
        "announcement": "Названа предварительная причина смерти пропавших в Омске сапбордистов",
        "status": None,
    },
    {
        "title": "Впустили лишь на опознание. С чем столкнулись владельцы электросамокатов",
        "source_url": "https://ria.ru/20260601/elektrosamokaty-2095083607.html",
        "source_domain": "ria.ru",
        "published_at": datetime.utcnow() - timedelta(hours=2),
        "announcement": "Названа предварительная причина смерти пропавших в Омске сапбордистов",
        "status": None,
    },
    {
        "title": "Скучно не будет: главные фестивали столичного лета — 2026",
        "source_url": "https://ria.ru/20260601/festivali-2095531450.html",
        "source_domain": "ria.ru",
        "published_at": datetime.utcnow() - timedelta(hours=2),
        "announcement": "Скучно не будет: главные фестивали столичного лета — 2026",
        "status": None,
    },
]


async def seed() -> None:
    async with AsyncSessionFactory() as session:
        created = 0
        for item in SAMPLE_NEWS:
            news = News(id=uuid.uuid4(), **item)
            session.add(news)
            created += 1

        await session.commit()
        print(f"✓ Mocked {created} news records in database")


if __name__ == "__main__":
    asyncio.run(seed())