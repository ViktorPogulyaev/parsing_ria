import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from core.utils import safe_int


@dataclass
class EnrichedData:
    """Нормализованный результат, возвращаемый парсером."""

    full_text: str | None = None
    author: str | None = None
    main_image_url: str | None = None
    images: list[dict[str, Any]] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    summary: str | None = None
    views_count: int | None = None
    comments_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_sufficient(self) -> bool:
        """True если есть полный текст."""
        return bool(self.full_text and len(self.full_text.strip()) > 100)

    def to_dict(self) -> dict[str, Any]:
        return {
            "full_text": self.full_text,
            "author": self.author,
            "main_image_url": self.main_image_url,
            "images": self.images,
            "categories": self.categories,
            "tags": self.tags,
            "keywords": self.keywords,
            "summary": self.summary,
            "views_count": self.views_count,
            "comments_count": self.comments_count,
            "metadata": self.metadata,
        }


class BaseParser(ABC):
    """Все парсеры должны реализовать этот интерфейс."""

    name: str = "base"

    @abstractmethod
    async def parse(self, url: str, html: str) -> EnrichedData:
        """Разбор полученного HTML и возвращение структурированных данных."""

    def supports(self, domain: str) -> bool:  # noqa: ARG002
        """True если этот парсер обрабатывает данный домен."""
        return False

    @staticmethod
    def clean_text(text: str | None) -> str | None:
        """Удаление избыточного пробелов из текста."""
        if not text:
            return None
        text = re.sub(r"\s+", " ", text)
        return text.strip() or None

    @staticmethod
    def extract_images_from_soup(soup: Any, base_url: str = "") -> list[dict]:
        """Извлечение изображений из HTML."""
        images = []
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = base_url.rstrip("/") + src
            if not src.startswith("http"):
                continue
            images.append(
                {
                    "url": src,
                    "caption": img.get("alt") or img.get("title"),
                    "width": safe_int(img.get("width")),
                    "height": safe_int(img.get("height")),
                }
            )
        return images


