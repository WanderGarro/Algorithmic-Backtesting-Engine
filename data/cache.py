from time import time
from core import Logger
from typing import Any, Optional

logger = Logger(__name__)

class DataCache:
    """
    Простой in-memory кэш для временного хранения финансовых данных.
    Кэш автоматически удаляет данные с истекшим сроком жизни при попытке доступа.
    Поддерживает настраиваемое время жизни записей и предоставляет статистику использования.

    Аргументы:
        default_timeout (int): Время жизни записей по умолчанию в секундах
        _cache (dict): Словарь для хранения кэшированных данных
        _timestamps (dict): Словарь для хранения временных меток истечения срока жизни

    Пример:
        >>> cache = DataCache(default_timeout=300)
        >>> cache.set("AAPL_price", 150.25)
        >>> price = cache.get("AAPL_price")
    """

    def __init__(self, default_timeout: int = 300):
        """
        Инициализация кэша.

        Аргументы:
            default_timeout (int): Время жизни записей по умолчанию в секундах (по умолчанию 300 = 5 минут)
        """
        self.default_timeout = default_timeout
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Получение данных из кэша по ключу.
        Если данные устарели или отсутствуют, возвращает None и автоматически удаляет устаревшие данные.

        Аргументы:
            key (str): Ключ для поиска в кэше

        Возвращает:
            Кэшированные данные или None, если данные отсутствуют или устарели

        Пример:
            >>> cache = DataCache(default_timeout=300)
            >>> value = cache.get("my_key")
        """
        if key not in self._cache:
            return None

        if self._is_expired(key):
            self.delete(key)
            return None

        logger.debug(f"Кэш попадание для ключа: {key}")
        return self._cache[key]

    def set(self, key: str, value: Any, timeout: Optional[int] = None):
        """
        Сохранение данных в кэш.

        Аргументы:
            key (str): Ключ для сохранения данных
            value (Any): Данные для кэширования (любой тип)
            timeout (Optional[int]): Время жизни в секундах (если None, используется default_timeout)

        Пример:
            >>> cache = DataCache(default_timeout=300)
            >>> cache.set("user_data", {"name": "John", "age": 30}, timeout=60)
        """
        timeout = timeout or self.default_timeout
        self._cache[key] = value
        self._timestamps[key] = time() + timeout
        logger.debug(f"Данные сохранены в кэш для ключа: {key}")

    def delete(self, key: str):
        """
        Удаление данных из кэша по ключу.

        Аргументы:
            key (str): Ключ данных для удаления

        Пример:
            >>> cache = DataCache(default_timeout=300)
            >>> cache.delete("obsolete_data")
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
        logger.debug(f"Данные удалены из кэша для ключа: {key}")

    def clear(self):
        """
        Полная очистка всего кэша.
        Удаляет все данные и временные метки.

        Пример:
            >>> cache = DataCache(default_timeout=300)
            >>> cache.clear()
            Кэш полностью очищен
        """
        self._cache.clear()
        self._timestamps.clear()
        logger.info("Кэш полностью очищен")

    def _is_expired(self, key: str) -> bool:
        """
        Проверяет, истекло ли время жизни данных.
        Internal метод для проверки срока годности записи.

        Аргументы:
            key (str): Ключ для проверки

        Возвращает:
            True если данные устарели, False если актуальны или отсутствуют
        """
        if key not in self._timestamps:
            return True

        return time() > self._timestamps[key]

    def get_stats(self) -> dict:
        """
        Возвращает статистику использования кэша.

        Возвращает:
            Словарь со статистикой:
                total_items: количество элементов в кэше
                cache_size: приблизительный размер кэша в символах

        Пример:
            >>> cache = DataCache(default_timeout=300)
            >>> stats = cache.get_stats()
        """
        return {'total_items': len(self._cache), 'cache_size': sum(len(str(v)) for v in self._cache.values()),}