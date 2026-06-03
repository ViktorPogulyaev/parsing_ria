# parsing-ria

Сервис сбора и обогащения новостей: REST API на FastAPI, фоновая обработка через Celery, хранение в PostgreSQL.

Поддерживаются фильтрация и полнотекстовый поиск, парсинг статей (сейчас — [ria.ru](https://ria.ru)), постановка задач обогащения в очередь Redis.

## Стек

- **Python 3.12+**, Poetry
- **FastAPI** + Uvicorn
- **SQLAlchemy 2** (async) + **asyncpg** + **Alembic**
- **Celery** + **Redis**
- **PostgreSQL 16**
- **httpx**, BeautifulSoup (основной парсер), newspaper3k (резервный парсер)


## Быстрый старт (Docker)

### 1. Переменные окружения

Скопируйте шаблон и заполните значения:

```bash
cp env.template.txt .env
```

### 2. Запуск

```bash
docker compose up -d --build
```

Сервисы:

| Сервис | Порт | Назначение |
|--------|------|------------|
| **api** | 8000 | REST API |
| **postgres** | 5432 | БД |
| **redis** | 6379 | брокер Celery |
| **worker** | — | обработка обогащения |
| **beat** | — | периодические задачи (расписание) |
| **flower** | 5555 | мониторинг Celery |

### 3. Миграции

Внутри Docker (рекомендуется, если в `.env` указан `POSTGRES_HOST=postgres`):

```bash
docker compose run --rm api alembic upgrade head
```

### 4. Документация API

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health: [http://localhost:8000/health](http://localhost:8000/health)

## Локальная разработка (без Docker для API)

```bash
poetry install
```

Поднимите только инфраструктуру:

```bash
docker compose up -d postgres redis
```

В `.env` для локального запуска укажите `POSTGRES_HOST=localhost` и `REDIS_HOST=localhost`.

```bash
POSTGRES_HOST=localhost alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Worker локально:

```bash
POSTGRES_HOST=localhost REDIS_HOST=localhost \
  poetry run celery -A app.broker.celery_app worker -l info -Q enrichment,default
```

## Миграции Alembic

```bash
# текущая ревизия
alembic current

# применить все
alembic upgrade head

# история
alembic history
```

Цепочка миграций:

1. `abce5b0de640` — таблица `news`
2. `778737c0c49e` — таблица `news_enrichment`


## Тестовые данные

```bash
POSTGRES_HOST=localhost poetry run python tests/scripts/mock_data.py
```
