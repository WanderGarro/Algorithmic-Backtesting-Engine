from indicators import RSI
from strategies import BaseStrategy
from pandas import DataFrame, Series

class RSIStrategy(BaseStrategy):
    """
    Классическая RSI стратегия на основе выхода из зон перекупленности/перепроданности.
    Осцилляторная стратегия, эффективная на боковых и ranging рынках.
    """

    def __init__(self, rsi_window: int = 14, overbought: int = 70, oversold: int = 30):
        """
        Инициализация RSI стратегии.

        Аргументы:
            rsi_window (int, optional): Период расчета RSI (по умолчанию 14)
            overbought (int, optional): Уровень перекупленности (по умолчанию 70)
            oversold (int, optional): Уровень перепроданности (по умолчанию 30)

        Применение:
        Альтернативные уровни для разных таймфреймов:
            Дневные: 70/30 (классические)
            Часовые: 80/20 (более строгие)
            Недельные: 65/35 (менее строгие)
        """
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация сигналов на основе выхода RSI из экстремальных зон.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: RSI выходит из зоны перепроданности (выше 30)
            🔴 Продажа: RSI выходит из зоны перекупленности (ниже 70)
            ➡️ Держать:

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = RSIStrategy()
        >>> trend_signals = strategy.generate_signals(prices)
        """
        rsi = RSI.calculate(data['close'], self.rsi_window)

        signals = Series(0, index=data.index)

        # Покупаем когда RSI выходит из зоны перепроданности
        signals[(rsi > self.oversold) & (rsi.shift(1) <= self.oversold)] = 1

        #  Продаем когда RSI выходит из зоны перекупленности
        signals[(rsi < self.overbought) & (rsi.shift(1) >= self.overbought)] = -1

        return signals

class RSIWithTrendStrategy(BaseStrategy):
    """
    Усовершенствованная RSI стратегия с учетом направления движения.
    Комбинирует перепроданность/перекупленность с моментумом для более точных сигналов.
    """

    def __init__(self, rsi_window: int = 14, overbought: int = 70, oversold: int = 30):
        """
        Инициализация RSI стратегии с учетом тренда.

        Аргументы:
            rsi_window (int, optional): Период расчета RSI (по умолчанию 14)
            overbought (int, optional): Уровень перекупленности (по умолчанию 70)
            oversold (int, optional): Уровень перепроданности (по умолчанию 30)
        """
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация сигналов с фильтрацией по направлению движения RSI.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: RSI в перепроданности (<30) И начинает расти
            🔴 Продажа: RSI в перекупленности (>70) И начинает падать
            ➡️ Держать:

        Плюсы:
            Фильтрация ложных сигналов
            Учет моментума индикатора
            Более ранние входы чем в классической стратегии

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = RSIWithTrendStrategy()
        >>> trend_signals = strategy.generate_signals(prices)
        """
        rsi = RSI.calculate(data['close'], self.rsi_window)

        signals = Series(0, index=data.index)

        # Покупаем когда RSI ниже 30 и начинает расти
        buy_condition = (rsi < self.oversold) & (rsi > rsi.shift(1))
        signals[buy_condition] = 1

        # Продаем когда RSI выше 70 и начинает падать
        sell_condition = (rsi > self.overbought) & (rsi < rsi.shift(1))
        signals[sell_condition] = -1

        return signals