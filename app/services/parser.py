from __future__ import annotations

import logging
import re

from bs4 import BeautifulSoup

from app.core.exceptions import ParserError
from app.services.base_parser import BaseParser, EnrichedData

logger = logging.getLogger(__name__)


# class Newspaper3kParser(BaseParser):
#     """Использование heuristics newspaper3k — должен работать на большинстве сайтов новостей."""
#
#     name = "newspaper3k"
#
#     async def parse(self, url: str, html: str) -> EnrichedData:
#         import newspaper
#
#         try:
#             article = newspaper.Article(url, language="ru")
#             article.set_html(html)
#             article.parse()
#             article.nlp()
#         except Exception as exc:
#             raise ParserError(f"newspaper3k failed: {exc}") from exc
#
#         data = EnrichedData(
#             full_text=self.clean_text(article.text),
#             author=", ".join(article.authors) if article.authors else None,
#             main_image_url=article.top_image or None,
#             keywords=list(article.keywords or []),
#             summary=self.clean_text(article.summary),
#         )
#
#         if article.top_img:
#             data.images = [{"url": article.top_img, "caption": None}]
#
#         return data


class RiaParser(BaseParser):
    """Парсер для сайта РИА Новости"""

    name = "ria"
    domains = {"ria.ru", "www.ria.ru"}

    async def parse(self, url: str, html: str) -> EnrichedData:
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception as exc:
            raise ParserError(str(exc)) from exc

        body = soup.select_one(".article__body, .article__text")
        if not body:
            raise ParserError("RiaParser: article body not found")

        for tag in body.select(".article__announce, .article__quote-author, script"):
            tag.decompose()

        full_text = self.clean_text(body.get_text(separator=" "))

        author_tag = soup.select_one(".article__author-name, .article__info-author a")
        author = self.clean_text(author_tag.get_text()) if author_tag else None

        img_tag = soup.select_one(".photoview__open img, .article__announce-img img")
        main_image = img_tag.get("src") if img_tag else None

        tags = [
            self.clean_text(t.get_text())
            for t in soup.select(".article__tags a")
            if t.get_text().strip()
        ]

        views = _parse_count(soup, ".statistic__item--views .statistic__value")
        comments = _parse_count(soup, ".statistic__item--comments .statistic__value")

        categories = [
            self.clean_text(c.get_text())
            for c in soup.select(".breadcrumb__item a")
            if c.get_text().strip()
        ]

        images = self.extract_images_from_soup(body, url)

        return EnrichedData(
            full_text=full_text,
            author=author,
            main_image_url=main_image,
            images=images,
            categories=[c for c in categories if c],
            tags=[t for t in tags if t],
            views_count=views,
            comments_count=comments,
        )


SITE_PARSERS: list[BaseParser] = [
    RiaParser(),
]


def get_parser_for_domain(domain: str) -> BaseParser | None:
    """Возвращает парсер для конкретного домена, или None."""
    for parser in SITE_PARSERS:
        if domain in getattr(parser, "domains", set()):
            return parser
    return None


def _parse_count(soup: BeautifulSoup, selector: str) -> int | None:
    """Извлечение количества из HTML."""
    tag = soup.select_one(selector)
    if not tag:
        return None
    text = tag.get_text(strip=True).replace("\xa0", "").replace(" ", "")
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None
