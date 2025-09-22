from abc import ABC, abstractmethod
from pandas import DataFrame, Series

class BaseStrategy(ABC):
    """Абстрактный базовый класс для всех торговых стратегий. Определяет интерфейс для генерации торговых сигналов."""
    @abstractmethod
    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация торговых сигналов на основе переданных данных.

        Аргументы:
            data (DataFrame): DataFrame с историческими данными, должен содержать колонку 'close' и опционально другие
                колонки (open, high, low, volume)

        Возвращает:
            Series: Серия торговых сигналов с тем же индексом, что и входные данные. Значения сигналов:
                        1 (BUY), -1 (SELL), 0 (HOLD/NO SIGNAL)

        Применение:
            Все конкретные стратегии должны реализовывать этот метод.
            Сигналы генерируются для каждого временного интервала в данных.
        """
        pass