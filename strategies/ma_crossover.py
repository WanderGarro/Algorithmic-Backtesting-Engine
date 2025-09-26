from indicators import EMA, SMA
from strategies import BaseStrategy
from pandas import DataFrame, Series

class SMACrossoverStrategy(BaseStrategy):
    """
    Стратегия пересечения простых скользящих средних (SMA).
    Генерирует сигналы на основе пересечения короткой и длинной SMA.
    Классическая трендовая стратегия, популярная среди трейдеров.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        Инициализация стратегии пересечения SMA.

        Аргументы:
            short_window (int, optional): Период короткой SMA (по умолчанию 20)
            long_window (int, optional): Период длинной SMA (по умолчанию 50)

        Применение:
            Краткосрочная торговля: Периоды 5-20
            Среднесрочная: Периоды 20-50
            Долгосрочная: Периоды 50-200
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация торговых сигналов на основе пересечения SMA.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: Короткая SMA пересекает длинную SMA снизу вверх
            🔴 Продажа: Короткая SMA пересекает длинную SMA сверху вниз
            ➡️ Держать: Нет пересечения или положение не изменилось

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = SMACrossoverStrategy(20, 50)
        >>> trend_signals = strategy.generate_signals(prices)
        """
        short_sma = SMA.calculate(data['close'], self.short_window)
        long_sma = SMA.calculate(data['close'], self.long_window)

        signals = Series(0, index=data.index)

        # Покупаем когда короткой период SMA выше длинного периода SMA
        signals[short_sma > long_sma] = 1

        # Продаем когда короткой период SMA ниже длинного периода SMA
        signals[short_sma < long_sma] = -1

        return signals

class EMACrossoverStrategy(BaseStrategy):
    """
    Стратегия пересечения экспоненциальных скользящих средних (EMA).
    Генерирует сигналы на основе пересечения короткой и длинной EMA.
    Более чувствительная версия SMA стратегии благодаря большему весу последних данных.
    """

    def __init__(self, short_window: int = 12, long_window: int = 26):
        """
        Инициализация стратегии пересечения EMA.

        Аргументы:
            short_window (int, optional) Период короткой EMA (по умолчанию 12)
            long_window (int, optional) Период длинной EMA (по умолчанию 26)

        Применение:
            Краткосрочная торговля: Периоды 5-20
            Среднесрочная: Периоды 20-50
            Долгосрочная: Периоды 50-200
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация торговых сигналов на основе пересечения EMA.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Серия с торговыми сигналами: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: Короткая EMA выше длинной EMA
            🔴 Продажа: Короткая EMA ниже длинной EMA
            ➡️ Держать:

        Плюсы:
            Быстрее реагирует на изменения тренда чем SMA
            Меньшая задержка сигналов
            Хорошо работает на трендовых рынках

        Минусы:
            Может давать ложные сигналы на боковых рынках
            Более чувствительна к рыночному шуму

       Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = EMACrossoverStrategy(12, 26)
        >>> trend_signals = strategy.generate_signals(prices)
        """
        # Вычисляем EMA
        short_ema = EMA.calculate(data['close'], self.short_window)
        long_ema = EMA.calculate(data['close'], self.long_window)

        # Создаем серию сигналов
        signals = Series(0, index=data.index)

        # Покупаем когда короткой период EMA выше длинного периода EMA
        signals[short_ema > long_ema] = 1

        # Продаем когда короткой период EMA ниже длинного периода EMA
        signals[short_ema < long_ema] = -1

        return signals