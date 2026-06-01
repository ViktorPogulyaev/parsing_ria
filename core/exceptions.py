class NotFoundError(Exception):
    """Исключение для случаев, когда объект не найден"""
    pass

class FetchError(Exception):
    """Исключение для случаев, когда возникает ошибка при получении данных"""
    pass

class ParserError(Exception):
    """Исключение для случаев, когда возникает ошибка при парсинге данных"""
    pass

class OutOfParsers(Exception):
    """Исключение для случаев, когда все парсеры проверены и ни один из них не смог обработать данные"""
    pass

class EnrichmentError(Exception):
    """Исключение для случаев, когда возникает ошибка при обогащении данных"""
    pass