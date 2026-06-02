from typing import Any


def safe_int(value: Any) -> int | None:
    """Безопасное преобразование значения в целое число."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
