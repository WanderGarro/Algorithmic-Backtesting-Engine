from .ema import EMA
from pandas import Series

class MACD:
    """Класс для расчета индикатора схождения/расхождения скользящих средних (MACD)"""
    @staticmethod
    def calculate(series: Series, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9) -> tuple:
        """
        Вычисляет индикатор MACD и его компоненты.
        MACD состоит из трех элементов:
            - MACD линия: разница между быстрой и медленной EMA
            - Сигнальная линия: EMA от MACD линии
            - Гистограмма: разница между MACD и сигнальной линией

        Аргументы:
            series (Series): Временной ряд данных для расчета. Обычно цены закрытия.
            fast_window (int, optional): Период быстрой EMA (по умолчанию 12)
            slow_window (int, optional): Период медленной EMA (по умолчанию 26)
            signal_window (int, optional): Период сигнальной EMA (по умолчанию 9)

        Возвращает:
            tuple (macd_line, signal_line, histogram):
                macd_line (Series): Линия MACD (fast_ema - slow_ema)
                signal_line (Series): Сигнальная линия (EMA от macd_line)
                histogram (Series): Гистограмма MACD (macd_line - signal_line)

        Компоненты индикатора:
            📊 MACD Line (синяя): Разница между 12- и 26-периодной EMA
            📈 Signal Line (красная): 9-периодная EMA от MACD Line
            📉 Histogram (столбики): Разница между MACD и Signal Line

        Основные сигналы:
            🎯 Пересечение линий:
                🟢 ПОКУПКА: MACD Line пересекает Signal Line снизу вверх
                🔴 ПРОДАЖА: MACD Line пересекает Signal Line сверху вниз

        📊 Положение относительно нуля:
            Выше нуля: Бычий тренд
            Ниже нуля: Медвежий тренд

        📈 Дивергенция (важный сигнал!):
            Бычья дивергенция: Цена делает более низкие минимумы, а MACD - более высокие"
            Медвежья дивергенция: Цена делает более высокие максимумы, а MACD - более низкие → разворот вниз

        📉 Анализ гистограммы:
            Растущие столбики: Усиление тренда
            Уменьшающиеся столбики: Ослабление тренда
            Смена направления: Возможный разворот

        Уровни перекупленности/перепроданности:
            Сильная перекупленность: MACD значительно выше нуля
            Сильная перепроданность: MACD значительно ниже нуля

        Торговые стратегии:
            Пересечение линий - основные торговые сигналы
            Дивергенция - опережающие сигналы разворота
            Пересечение нулевой линии - смена тренда
            Анализ гистограммы - сила текущего движения
        """
        fast_ema = EMA.calculate(series, fast_window)
        slow_ema = EMA.calculate(series, slow_window)
        macd_line = fast_ema - slow_ema
        signal_line = EMA.calculate(macd_line, signal_window)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram