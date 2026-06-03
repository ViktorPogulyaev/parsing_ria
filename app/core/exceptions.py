class AppError(Exception):
    """Базовое исключение с текстом для логов и ответов API."""

    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Объект не найден в БД."""


class EnrichmentPipelineError(AppError):
    """Ошибка на одном из этапов обогащения новости."""


class FetchError(EnrichmentPipelineError):
    """Не удалось получить HTML (сеть, таймаут, HTTP ≠ 2xx)."""


class ParserError(EnrichmentPipelineError):
    """Парсер не смог извлечь данные из HTML."""


class OutOfParsersError(EnrichmentPipelineError):
    """Нет парсера для домена или все парсеры вернули ошибку/мало текста."""


class EnrichmentError(EnrichmentPipelineError):
    """Обогащение не завершено (обёртка для worker и внешних вызовов)."""


__all__ = [
    "AppError",
    "EnrichmentError",
    "EnrichmentPipelineError",
    "FetchError",
    "NotFoundError",
    "OutOfParsers",
    "ParserError",
]
