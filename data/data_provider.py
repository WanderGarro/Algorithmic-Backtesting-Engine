from pandas import DataFrame
from abc import ABC, abstractmethod

class DataProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров данных"""
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1d') -> DataFrame:
        """
        Получение исторических данных

        Аргументы:
            symbol (str): Тикер акции (например, 'AAPL')
            start_date (str): Начальная дата в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата в формате 'YYYY-MM-DD'
            interval (str): Интервал данных ('1d', '1h', etc.)

        Возвращает:
            DataFrame с колонками: ['open', 'high', 'low', 'close', 'volume']
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Получение текущей цены"""
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> dict:
        """Получение информации о компании"""
        pass