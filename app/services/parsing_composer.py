"""Обогащение данных новостей.

Стратегия (chain-of-responsibility):
  Парсер для конкретного сайта (если домен известен)


Цепочка парсеров проходит последовательно каждый парсер (в нашем случае это только RiaParser).
Если парсер вызывает ParserError или возвращает данные, которые не являются "достаточными" (< 100 символов текста),
то он переходит к следующему парсеру (в нашем случае выбрасывает ошибку OutOfParsers).
Если возникает FetchError, то нет смысла пытать другие парсеры, так как до ресурса достучаться не получается.

"""

import logging
from urllib.parse import urlparse
import asyncio

from app.core.exceptions import EnrichmentError, FetchError, ParserError
from app.models.news import News
from app.services.base_parser import BaseParser, EnrichedData
from app.services.fetcher import get_fetcher
from app.services.parser import get_parser_for_domain
from app.services.nlp import (extract_keywords, generate_summary, estimate_reading_time)

logger = logging.getLogger(__name__)


class EnrichmentComposer:
    """Оркестрирует получение, парсинг и пост-обработку данных новостей."""

    def _build_chain(self, domain: str) -> list[BaseParser]:
        """Построение цепочки парсеров."""
        chain: list[BaseParser] = []
        site_parser = get_parser_for_domain(domain)
        if site_parser:
            chain.append(site_parser)
        return chain

    async def enrich(self, news: News) -> tuple[EnrichedData, str]:
        """Обогащение данных новости.

        Возвращает (EnrichedData, parser_name_used).
        Выбрасывает EnrichmentError, если все парсеры провалились или не удалось получить доступ к ресурсу.
        """
        url = news.source_url
        domain = urlparse(url).netloc.lstrip("www.")

        fetcher = get_fetcher()
        try:
            html, final_url = await fetcher.fetch(url)
        except FetchError as exc:
            raise EnrichmentError(
                f"Не удалось получить доступ к ресурсу {url}: {exc}"
            ) from exc

        chain = self._build_chain(domain)
        last_error: Exception | None = None

        for parser in chain:
            try:
                data = await parser.parse(final_url, html)
                data = await asyncio.to_thread(self._post_process, data, html)
                if data.is_sufficient():
                    logger.info("Парсер %r успешно обработал %s", parser.name, url)
                    return data, parser.name
                else:
                    logger.debug(
                        "Парсер %r вернул недостаточные данные для %s, пробуем следующий",
                        parser.name,
                        url,
                    )
            except ParserError as exc:
                logger.warning("Парсер %r упал для %s: %s", parser.name, url, exc)
                last_error = exc
                continue


    def _post_process(self, data: EnrichedData, html: str) -> EnrichedData:
        """Добавление NLP полей к данным новости."""
        text = data.full_text or ""
 
        if not data.keywords and text:
            data.keywords = extract_keywords(text)
 
        if not data.summary and text:
            data.summary = generate_summary(text)
 
        # Metadata enrichments
        data.article_metadata["reading_time_minutes"] = estimate_reading_time(text)
 
        return data