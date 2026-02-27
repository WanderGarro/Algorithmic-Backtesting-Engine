from indicators import RSI, MACD
from strategies import BaseStrategy
from pandas import DataFrame, Series

class CombinedRSIMACDStrategy(BaseStrategy):
    """
    Комбинированная стратегия RSI + MACD для фильтрации сигналов.
    Сочетает трендовый индикатор (MACD) и осциллятор (RSI) для получения
    более качественных и отфильтрованных торговых сигналов.
    """

    def __init__(self, rsi_window: int = 14, overbought: int = 70, oversold: int = 30,
                                                        macd_fast: int = 12,macd_slow: int = 26, macd_signal: int = 9):
        """
        Инициализация комбинированной стратегии.

        Аргументы:
            rsi_window (int, optional): Период RSI (по умолчанию 14)
            overbought (int, optional): Уровень перекупленности RSI (по умолчанию 70)
            oversold (int, optional): Уровень перепроданности RSI (по умолчанию 30)
            macd_fast (int, optional): Период быстрой EMA MACD (по умолчанию 12)
            macd_slow (int, optional): Период медленной EMA MACD (по умолчанию 26)
            macd_signal (int, optional): Период сигнальной EMA MACD (по умолчанию 9)
        """
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация сигналов с двойным подтверждением от RSI и MACD.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: RSI в перепроданности И MACD выше сигнальной (бычий моментум)
            🔴 Продажа: RSI в перекупленности И MACD ниже сигнальной (медвежий моментум)
            ➡️ Держать:

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = CombinedRSIMACDStrategy()
        >>> trend_signals = strategy.generate_signals(prices)
        """
        # Рассчитываем индикаторы
        rsi = RSI.calculate(data['close'], self.rsi_window)
        macd_line, signal_line, _ = MACD.calculate(data['close'], self.macd_fast, self.macd_slow, self.macd_signal)

        signals = Series(0, index=data.index)

        # Покупаем когда RSI в зоне перепроданности И MACD выше сигнальной линии
        buy_condition = (rsi < self.oversold) & (macd_line > signal_line)
        signals[buy_condition] = 1

        # Продаем когда в зоне перекупленности И MACD ниже сигнальной линии
        sell_condition = (rsi > self.overbought) & (macd_line < signal_line)
        signals[sell_condition] = -1

        return signals