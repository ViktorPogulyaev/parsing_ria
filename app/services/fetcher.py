
# from __future__ import annotations

import asyncio
import logging
import random
from urllib.parse import urlparse

import httpx
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from app.configuration.config import settings
from app.core.exceptions import FetchError

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": settings.enrichment_user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
}


class Fetcher:
    """Общий асинхронный HTTP клиент с поддержкой пула соединений."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Получение клиента HTTP."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=HEADERS,
                timeout=httpx.Timeout(settings.enrichment_request_timeout),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def fetch(self, url: str) -> tuple[str, str]:
        """Получение URL и возвращение (html, final_url).

        Вызывает FetchError при не-2xx статуса.
        """
        # Задержка: 0.5–2 секунды на домен
        await asyncio.sleep(random.uniform(0.5, 2.0))  # noqa: S311

        client = await self._get_client()
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise FetchError(
                f"HTTP {exc.response.status_code} for {url}"
            ) from exc
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            logger.warning("Fetch error for %s: %s", url, exc)
            raise

        encoding = response.encoding or "utf-8"
        html = response.content.decode(encoding, errors="replace")
        return html, str(response.url)

    async def aclose(self) -> None:
        """Закрытие асинхронного клиента HTTP."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Делаем HTTP клиент singleton-ом
_fetcher: Fetcher | None = None


def get_fetcher() -> Fetcher:
    """Получение singleton-клиента HTTP."""
    global _fetcher  # noqa: PLW0603
    if _fetcher is None:
        _fetcher = Fetcher()
    return _fetcher
    