class NotFoundError(Exception):
    """Исключение для случаев, когда объект не найден"""
    pass

class FetchError(Exception):
    """Исключение для случаев, когда возникает ошибка при получении данных"""
    pass

class ParserError(Exception):
    """Исключение для случаев, когда возникает ошибка при парсинге данных"""
    pass