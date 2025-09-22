from indicators import MACD
from pandas import DataFrame, Series
from base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """
    Классическая MACD стратегия на основе пересечения MACD и сигнальной линий.
    Одна из самых популярных стратегий технического анализа среди трейдеров.
    """

    def __init__(self, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9):
        """
        Инициализация MACD стратегии.

        Аргументы:
            fast_window (int, optional): Период быстрой EMA (по умолчанию 12)
            slow_window : int, optional): Период медленной EMA (по умолчанию 26)
            signal_window : int, optional): Период сигнальной EMA (по умолчанию 9)
        """
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_window = signal_window

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация сигналов на основе пересечения MACD и сигнальной линий.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: MACD линия пересекает сигнальную снизу вверх
            🔴 Продажа: MACD линия пересекает сигнальную сверху вниз
            ➡️ Держать:

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = MACDStrategy()
        >>> trend_signals = strategy.generate_signals(prices)
        """
        macd_line, signal_line, _ = MACD.calculate(data['close'],self.fast_window,self.slow_window,self.signal_window)

        signals = Series(0, index=data.index)

        # Покупаем когда MACD пересекает сигнальную линию снизу вверх
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 1

        # Продаем когда MACD пересекает сигнальную линию сверху вниз
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = -1

        return signals

class MACDZeroCrossStrategy(BaseStrategy):
    """
    MACD стратегия с пересечением нулевой линии.
    Альтернативный подход к торговле по MACD, фокусирующийся на смене тренда при пересечении нулевого уровня.
    """

    def __init__(self, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9):
        """
        Инициализация стратегии пересечения нулевой линии MACD.

        Аргументы:
            fast_window (int, optional): Период быстрой EMA (по умолчанию 12)
            slow_window : int, optional): Период медленной EMA (по умолчанию 26)
            signal_window : int, optional): Период сигнальной EMA (по умолчанию 9)
        """
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.signal_window = signal_window

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация сигналов на основе пересечения MACD нулевой линии.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: MACD линия пересекает сигнальную снизу вверх
            🔴 Продажа: MACD линия пересекает сигнальную сверху вниз
            ➡️ Держать:

        Плюсы:
            Меньше ложных сигналов чем при пересечении линий
            Ловит основные развороты тренда
            Простая интерпретация

        Минусы:
            Поздние сигналы (вход уже после начала тренда)
            Может пропускать короткие движения

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = MACDZeroCrossStrategy()
        >>> trend_signals = strategy.generate_signals(prices)
        """
        macd_line, signal_line, _ = MACD.calculate(data['close'],self.fast_window,self.slow_window,self.signal_window)

        signals = Series(0, index=data.index)

        # Покупаем когда MACD пересекает ноль снизу вверх
        signals[(macd_line > 0) & (macd_line.shift(1) <= 0)] = 1

        # Продаем когда MACD пересекает ноль сверху вниз
        signals[(macd_line < 0) & (macd_line.shift(1) >= 0)] = -1

        return signals