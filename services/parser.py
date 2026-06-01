import logging
import newspaper
from core.exceptions import ParserError
from services.base_parser import BaseParser, EnrichedData

logger = logging.getLogger(__name__)


class Newspaper3kParser(BaseParser):
    """Использование heuristics newspaper3k — должен работать на большинстве сайтов новостей."""

    name = "newspaper3k"

    async def parse(self, url: str, html: str) -> EnrichedData:
        try:
            article = newspaper.Article(url, language="ru")
            article.set_html(html)
            article.parse()
            article.nlp()
        except Exception as exc:
            raise ParserError(f"newspaper3k failed: {exc}") from exc

        data = EnrichedData(
            full_text=self.clean_text(article.text),
            author=", ".join(article.authors) if article.authors else None,
            main_image_url=article.top_image or None,
            keywords=list(article.keywords or []),
            summary=self.clean_text(article.summary),
        )

        if article.top_img:
            data.images = [{"url": article.top_img, "caption": None}]

        return data


class ReserveParser(BaseParser):
    """Резервный парсер"""
    def parse(self, url: str, html: str) -> EnrichedData:
        raise ParserError("Резервный парсер не реализован")