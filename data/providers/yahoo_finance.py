from core import Logger
from yfinance import Ticker
from pandas import DataFrame
from data.cache import DataCache
from typing import Dict, Optional
from data.data_provider import DataProvider

logger = Logger(__name__)

class YahooFinanceProvider(DataProvider):
    """
    Провайдер для получения финансовых данных из Yahoo Finance API.
    Класс предоставляет интерфейс для загрузки исторических данных,
    текущих цен и информации о компаниях с поддержкой кэширования.

    Аргументы:
        cache (Optional[DataCache]): Специализированный класс для хранения кэшированных данных
        cache_timeout (int): Время жизни кэша в секундах (по умолчанию 300 секунд)

    Пример:
        >>> provider = YahooFinanceProvider()
        >>> data = provider.get_historical_data('AAPL', '2023-01-01', '2023-12-31')
        >>> price = provider.get_current_price('AAPL')
        >>> info = provider.get_company_info('AAPL')
    """

    def __init__(self, cache: Optional[DataCache] = None, cache_timeout: int = 300):
        """
        Инициализация провайдера Yahoo Finance.

        Аргументы:
            cache (Optional[DataCache]): Специализированный для хранения кэшированных данных
            cache_timeout (int, optional): Время жизни кэша в секундах. По умолчанию 300 секунд (5 минут).
        """
        self.cache_timeout = cache_timeout
        self.cache = cache or DataCache(default_timeout=cache_timeout)

    def get_historical_data(self, symbol: str, start_date: str, end_date: str, interval: str = '1d') -> DataFrame:
        """
        Получает исторические данные по акции за указанный период.

        Аргументы:
            symbol (str): Тикер акции (например, 'AAPL', 'GOOGL')
            start_date (str): Начальная дата в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата в формате 'YYYY-MM-DD'
            interval (str, optional): Интервал данных. Доступные значения: '1d', '1wk', '1mo'. По умолчанию '1d'

        Возвращает:
            DataFrame: DataFrame с историческими данными, содержащий колонки:
                open: Цена открытия
                high: Максимальная цена
                low: Минимальная цена
                close: Цена закрытия
                volume: Объем торгов
                symbol: Тикер акции
                date: Дата

        Ошибки:
            ValueError: Если данные не найдены или отсутствуют необходимые колонки
            Exception: При ошибках загрузки данных

        Пример:
            >>> provider = YahooFinanceProvider()
            >>> provider_data = provider.get_historical_data('AAPL', '2023-01-01', '2023-12-31')
        """
        try:
            cache_key = f"historical_{symbol}_{start_date}_{end_date}_{interval}"

            # Используем универсальный кэш
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            logger.info(f"Загружаем данные для {symbol} с {start_date} по {end_date}")

            # Загружаем данные
            ticker = Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)

            if data.empty:
                raise ValueError(f"Не удалось загрузить данные для {symbol}")

            # Проверяем необходимые колонки
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in data.columns:
                    raise ValueError(f"Отсутствует колонка {col} в данных")

            # Переименовываем колонки для consistency
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Добавляем тикер и дату как индекс
            data['symbol'] = symbol
            data['date'] = data.index

            # Заполняем пропущенные значения
            data = self._fill_missing_data(data)

            # Сохраняем в кэш
            logger.info(f"Успешно загружено {len(data)} записей для {symbol}")
            self.cache.set(cache_key, data)
            return data

        except Exception as e:
            logger.error(f"Ошибка при загрузке данных для {symbol}: {str(e)}")
            raise

    def get_multiple_symbols(self, symbols: list, start_date: str, end_date: str) -> Dict[str, DataFrame]:
        """
        Получает исторические данные для нескольких тикеров одновременно.

        Аргументы:
            symbols (list): Список тикеров
            start_date (str): Начальная дата в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата в формате 'YYYY-MM-DD'

        Возвращает:
            Dict[str, DataFrame]: Словарь, где ключи - тикеры, значения - DataFrame с данными.
                Для тикеров с ошибками возвращается пустой DataFrame.

        Пример:
            >>> provider = YahooFinanceProvider()
            >>> provider_symbols = ['AAPL', 'GOOGL', 'MSFT']
            >>> data_dict = provider.get_multiple_symbols(provider_symbols, '2023-01-01', '2023-12-31')
        """
        results = {}
        for symbol in symbols:
            try:
                data = self.get_historical_data(symbol, start_date, end_date)
                results[symbol] = data
            except Exception as e:
                logger.error(f"Ошибка при загрузке {symbol}: {str(e)}")
                results[symbol] = DataFrame()

        return results

    def get_current_price(self, symbol: str) -> float:
        """
        Получает текущую цену акции.

        Аргументы:
            symbol (str): Тикер акции

        Возвращает:
            float: Текущая цена акции. Возвращает 0.0 в случае ошибки.

        Пример:
            >>> provider = YahooFinanceProvider()
            >>> provider_price = provider.get_current_price('AAPL')
        """
        cache_key = f"current_price_{symbol}"
        cached_price = self.cache.get(cache_key)
        if cached_price is not None:
            return cached_price

        try:
            ticker = Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))

            self.cache.set(cache_key, price, timeout=60)  # Короткий TTL для цен
            return price
        except Exception as e:
            logger.error(f"Ошибка при получении цены для {symbol}: {str(e)}")
            return 0.0

    def get_company_info(self, symbol: str) -> Dict:
        """
        Получает основную информацию о компании.

        Аргументы:
            symbol (str): Тикер акции

        Возвращает:
            Dict: Словарь с информацией о компании, содержащий:
                name: Полное название компании
                sector: Сектор экономики
                industry: Отрасль
                market_cap: Рыночная капитализация
                pe_ratio: P/E коэффициент
                dividend_yield: Дивидендная доходность
                description: Описание компании

        Пример:
            >>> provider = YahooFinanceProvider()
            >>> provider_info = provider.get_company_info('AAPL')
        """
        cache_key = f"company_info_{symbol}"
        cached_info = self.cache.get(cache_key)
        if cached_info is not None:
            return cached_info

        try:
            ticker = Ticker(symbol)
            info = ticker.info

            company_info = {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'description': info.get('longBusinessSummary', ''),
            }

            self.cache.set(cache_key, company_info, timeout=3600)  # Длинный TTL
            return company_info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о {symbol}: {str(e)}")
            return {}

    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Проверяет существование тикера в Yahoo Finance.

        Аргументы:
            symbol (str): Тикер для проверки

        Возвращает:
            bool: True если тикер существует, False в противном случае

        Пример:
            >>> provider = YahooFinanceProvider()
            >>> if provider.validate_symbol('AAPL'):
            ...     print("Тикер существует")
            ... else:
            ...     print("Тикер не найден")
        """
        try:
            ticker = Ticker(symbol)
            info = ticker.info
            return info is not None and len(info) > 0
        except:
            return False

    @staticmethod
    def _fill_missing_data(data: DataFrame) -> DataFrame:
        """
        Заполняет пропущенные значения в данных.

        Аргументы:
            data (DataFrame): Исходные данные с пропусками

        Возвращает:
            DataFrame: Данные с заполненными пропусками
        """
        # Forward fill для цен
        price_columns = ['open', 'high', 'low', 'close']
        data[price_columns] = data[price_columns].fillna(method='ffill')

        # Заполнение объема нулями
        data['volume'] = data['volume'].fillna(0)

        return data