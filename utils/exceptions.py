class ParserException(Exception):
    detail = "❌ Main Error"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class CookiesFileNotFoundError(ParserException):
    detail = "❌ Файл Cookies не найден. Работа программы остановлена"


class ProductsListFileNotFoundError(ParserException):
    detail = "❌ Файл c ID товаров не найден. Работа программы остановлена"


class ProductsIDsNotFoundError(ParserException):
    detail = "❌ ID товаров не найдены. Работа программы остановлена"


class ProductsListIDsNotFoundError(ParserException):
    detail = "❌ Лист с ID для парсинга не найден. Работа программы остановлена"
