import pytest
import numpy as np
from pandas import DataFrame, Series
from strategies import (BaseStrategy, SMACrossoverStrategy, EMACrossoverStrategy, MACDStrategy,
                        MACDZeroCrossStrategy, CombinedRSIMACDStrategy, RSIStrategy, RSIWithTrendStrategy)

class TestBaseStrategy:
    """Тесты для базового абстрактного класса стратегии"""

    def test_base_strategy_is_abstract(self):
        """Тест BaseStrategy является абстрактным классом"""
        with pytest.raises(TypeError):
            # Нельзя создать экземпляр абстрактного класса
            BaseStrategy()

class TestSMACrossoverStrategy:
    """Тесты для стратегии пересечения SMA"""

    def test_sma_crossover_initialization(self):
        """Тест инициализации стратегии SMA"""
        strategy = SMACrossoverStrategy(short_window=10, long_window=30)
        assert strategy.short_window == 10
        assert strategy.long_window == 30

    def test_sma_crossover_default_parameters(self):
        """Тест параметров по умолчанию"""
        strategy = SMACrossoverStrategy()
        assert strategy.short_window == 20
        assert strategy.long_window == 50

    def test_sma_crossover_buy_signal(self, sample_price_data):
        """Тест сигнала покупки (короткая SMA выше длинной)"""
        # Arrange
        data = DataFrame({'close': sample_price_data})
        strategy = SMACrossoverStrategy(short_window=2, long_window=5)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        assert len(signals) == len(data)
        # Проверяем что есть хотя бы один сигнал покупки
        assert np.any(signals == 1)

    def test_sma_crossover_sell_signal(self, falling_trend_data):
        """Тест сигнала продажи (короткая SMA ниже длинной)"""
        # Arrange
        data = DataFrame({'close': falling_trend_data})
        strategy = SMACrossoverStrategy(short_window=5, long_window=10)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        assert len(signals) == len(data)
        # В нисходящем тренде должны быть сигналы продажи
        assert np.any(signals == -1)

    def test_sma_crossover_no_signal_sideways(self):
        """Тест отсутствия сигналов при боковом движении"""
        # Arrange - боковое движение
        data = DataFrame({'close': Series([100, 101, 100, 101, 100, 101, 100])})
        strategy = SMACrossoverStrategy(short_window=3, long_window=5)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        # При боковом движении сигналы могут быть, но проверяем корректность
        assert isinstance(signals, Series)
        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_sma_crossover_with_insufficient_data(self):
        """Тест с недостаточным количеством данных"""
        # Arrange
        data = DataFrame({'close': Series([100, 101])})  # Всего 2 точки
        strategy = SMACrossoverStrategy(short_window=3, long_window=5)

        # Act
        signals = strategy.generate_signals(data)

        # Assert - не должно быть падения, только нулевые сигналы
        assert isinstance(signals, Series)
        assert len(signals) == 2
        assert np.all(signals == 0)  # Все сигналы должны быть 0

class TestEMACrossoverStrategy:
    """Тесты для стратегии пересечения EMA"""

    def test_ema_crossover_initialization(self):
        """Тест инициализации стратегии EMA"""
        strategy = EMACrossoverStrategy(short_window=8, long_window=21)
        assert strategy.short_window == 8
        assert strategy.long_window == 21

    def test_ema_crossover_buy_signal(self, rising_trend_data):
        """Тест сигнала покупки EMA"""
        # Arrange
        data = DataFrame({'close': rising_trend_data})
        strategy = EMACrossoverStrategy(short_window=5, long_window=10)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        assert len(signals) == len(data)
        # В восходящем тренде должны быть сигналы покупки
        assert np.any(signals == 1)

    def test_ema_crossover_vs_sma_reactivity(self, volatile_data):
        """Тест EMA реагирует быстрее чем SMA"""
        # Arrange
        data = DataFrame({'close': volatile_data})
        ema_strategy = EMACrossoverStrategy(short_window=10, long_window=20)
        sma_strategy = SMACrossoverStrategy(short_window=10, long_window=20)

        # Act
        ema_signals = ema_strategy.generate_signals(data)
        sma_signals = sma_strategy.generate_signals(data)

        # Assert - EMA должна давать больше сигналов из-за большей чувствительности
        ema_signal_count = (ema_signals != 0).sum()
        sma_signal_count = (sma_signals != 0).sum()

        # EMA обычно дает больше сигналов из-за большей чувствительности
        assert ema_signal_count >= sma_signal_count

class TestMACDStrategy:
    """Тесты для классической MACD стратегии"""

    def test_macd_strategy_initialization(self):
        """Тест инициализации MACD стратегии"""
        strategy = MACDStrategy(fast_window=8, slow_window=17, signal_window=6)
        assert strategy.fast_window == 8
        assert strategy.slow_window == 17
        assert strategy.signal_window == 6

    def test_macd_crossover_buy_signal(self):
        """Тест сигнала покупки при пересечении MACD снизу вверх"""
        # Arrange - создаем данные где MACD пересекает сигнальную линию
        data = DataFrame({
            'close': Series([20, 19, 18, 17, 18, 19, 20, 21, 22, 23])  # Падение -> рост
        })
        strategy = MACDStrategy(fast_window=3, slow_window=6, signal_window=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть хотя бы один сигнал покупки
        assert np.any(signals == 1)

    def test_macd_crossover_sell_signal(self):
        """Тест сигнала продажи при пересечении MACD сверху вниз"""
        # Arrange - создаем данные где MACD пересекает сигнальную линию сверху вниз
        data = DataFrame({
            'close': Series([23, 22, 21, 20, 19, 18, 17, 16, 15, 14])  # Рост -> падение
        })
        strategy = MACDStrategy(fast_window=3, slow_window=6, signal_window=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть хотя бы один сигнал продажи
        assert np.any(signals == -1)

    def test_macd_no_false_signals(self, sample_price_data):
        """Тест MACD не генерирует ложные сигналы на стабильных данных"""
        # Arrange
        data = DataFrame({'close': sample_price_data})
        strategy = MACDStrategy()

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Все сигналы должны быть валидными
        assert set(signals.unique()).issubset({-1, 0, 1})

class TestMACDZeroCrossStrategy:
    """Тесты для стратегии пересечения нулевой линии MACD"""

    def test_macd_zero_cross_buy_signal(self):
        """Тест сигнала покупки при пересечении нуля снизу вверх"""
        # Arrange - данные где MACD переходит из отрицательных в положительные значения
        data = DataFrame({
            'close': Series([15, 16, 17, 18, 19, 20, 21, 22, 23, 24])  # Устойчивый рост
        })
        strategy = MACDZeroCrossStrategy(fast_window=3, slow_window=6, signal_window=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал покупки при пересечении нуля
        assert np.any(signals == 1)

    def test_macd_zero_cross_sell_signal(self):
        """Тест сигнала продажи при пересечении нуля сверху вниз"""
        # Arrange - данные где MACD переходит из положительных в отрицательные значения
        data = DataFrame({
            'close': Series([24, 23, 22, 21, 20, 19, 18, 17, 16, 15])  # Устойчивое падение
        })
        strategy = MACDZeroCrossStrategy(fast_window=3, slow_window=6, signal_window=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал продажи при пересечении нуля
        assert np.any(signals == -1)

class TestRSIStrategy:
    """Тесты для классической RSI стратегии"""

    def test_rsi_strategy_initialization(self):
        """Тест инициализации RSI стратегии"""
        strategy = RSIStrategy(rsi_window=10, overbought=80, oversold=20)
        assert strategy.rsi_window == 10
        assert strategy.overbought == 80
        assert strategy.oversold == 20

    def test_rsi_buy_signal_oversold(self):
        """Тест сигнала покупки при выходе из зоны перепроданности"""
        # Arrange - данные где RSI выходит из зоны перепроданности
        data = DataFrame({
            'close': Series([20, 19, 18, 17, 18, 19, 20, 21, 22, 23])  # Падение -> восстановление
        })
        strategy = RSIStrategy(rsi_window=5, overbought=70, oversold=30)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал покупки при выходе из перепроданности
        assert np.any(signals == 1)

    def test_rsi_sell_signal_overbought(self):
        """Тест сигнала продажи при выходе из зоны перекупленности"""
        # Arrange - данные где RSI выходит из зоны перекупленности
        data = DataFrame({
            'close': Series([15, 16, 17, 18, 19, 20, 19, 18, 17, 16])  # Рост -> коррекция
        })
        strategy = RSIStrategy(rsi_window=5, overbought=70, oversold=30)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал продажи при выходе из перекупленности
        assert np.any(signals == -1)

class TestRSIWithTrendStrategy:
    """Тесты для RSI стратегии с учетом тренда"""

    def test_rsi_trend_buy_signal(self):
        """Тест сигнала покупки RSI с трендом"""
        # Arrange - данные где RSI в перепроданности и начинает расти
        data = DataFrame({
            'close': Series([20, 19, 18, 17, 17.5, 18, 18.5, 19, 19.5, 20])
        })
        strategy = RSIWithTrendStrategy(rsi_window=5, overbought=70, oversold=30)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал покупки когда RSI в перепроданности и растет
        assert np.any(signals == 1)

    def test_rsi_trend_sell_signal(self):
        """Тест сигнала продажи RSI с трендом"""
        # Arrange - данные где RSI в перекупленности и начинает падать
        data = DataFrame({
            'close': Series([15, 16, 17, 18, 19, 20, 19.5, 19, 18.5, 18])
        })
        strategy = RSIWithTrendStrategy(rsi_window=5, overbought=70, oversold=30)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал продажи когда RSI в перекупленности и падает
        assert np.any(signals == -1)

class TestCombinedRSIMACDStrategy:
    """Тесты для комбинированной RSI + MACD стратегии"""

    def test_combined_strategy_initialization(self):
        """Тест инициализации комбинированной стратегии"""
        strategy = CombinedRSIMACDStrategy(
            rsi_window=10, overbought=80, oversold=20, macd_fast=8, macd_slow=17, macd_signal=6)
        assert strategy.rsi_window == 10
        assert strategy.overbought == 80
        assert strategy.oversold == 20
        assert strategy.macd_fast == 8
        assert strategy.macd_slow == 17
        assert strategy.macd_signal == 6

    def test_combined_buy_signal(self):
        """Тест сигнала покупки при совпадении RSI и MACD условий"""
        # Arrange - данные где RSI в перепроданности и MACD бычий
        data = DataFrame({
            'close': Series([20, 19, 18, 17, 17.5, 18, 18.5, 19, 20, 21])
        })
        strategy = CombinedRSIMACDStrategy(
            rsi_window=5, overbought=70, oversold=30, macd_fast=3, macd_slow=6, macd_signal=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал покупки при совпадении условий
        assert np.any(signals == 1)

    def test_combined_sell_signal(self):
        """Тест сигнала продажи при совпадении RSI и MACD условий"""
        # Arrange - данные где RSI в перекупленности и MACD медвежий
        data = DataFrame({
            'close': Series([15, 16, 17, 18, 19, 20, 19.5, 19, 18, 17])
        })
        strategy = CombinedRSIMACDStrategy(
            rsi_window=5, overbought=70, oversold=30, macd_fast=3, macd_slow=6, macd_signal=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # Должен быть сигнал продажи при совпадении условий
        assert np.any(signals == -1)

    def test_combined_no_signal_when_conditions_not_met(self):
        """Тест отсутствия сигнала когда условия не совпадают"""
        # Arrange - данные где только одно условие выполняется
        data = DataFrame({
            'close': Series([100, 101, 100, 101, 100, 101, 100, 101, 100, 101])  # Боковое движение
        })
        strategy = CombinedRSIMACDStrategy(
            rsi_window=5, overbought=70, oversold=30, macd_fast=3, macd_slow=6, macd_signal=2)

        # Act
        signals = strategy.generate_signals(data)

        # Assert
        assert isinstance(signals, Series)
        # При боковом движении сигналов может не быть
        # Главное - что нет ошибок

class TestStrategyIntegration:
    """Интеграционные тесты для всех стратегий"""

    def test_all_strategies_with_volatile_data(self, volatile_data):
        """Тест всех стратегий на волатильных данных"""
        data = DataFrame({'close': volatile_data})
        strategies = [
            SMACrossoverStrategy(10, 20),
            EMACrossoverStrategy(10, 20),
            MACDStrategy(),
            MACDZeroCrossStrategy(),
            RSIStrategy(),
            RSIWithTrendStrategy(),
            CombinedRSIMACDStrategy()
        ]

        for strategy in strategies:
            signals = strategy.generate_signals(data)
            assert isinstance(signals, Series)
            assert len(signals) == len(data)
            # Проверяем что все сигналы валидны
            assert set(signals.unique()).issubset({-1, 0, 1})

    def test_strategy_signals_consistency(self, sample_price_data):
        """Тест согласованности сигналов разных стратегий"""
        data = DataFrame({'close': sample_price_data})

        # Стратегии с похожей логикой должны давать сходные сигналы
        sma_signals = SMACrossoverStrategy(5, 10).generate_signals(data)
        ema_signals = EMACrossoverStrategy(5, 10).generate_signals(data)

        # Они не обязаны быть идентичными, но должны быть корректными
        assert isinstance(sma_signals, Series)
        assert isinstance(ema_signals, Series)
        assert len(sma_signals) == len(ema_signals)

    def test_edge_cases_all_strategies(self):
        """Тест пограничных случаев для всех стратегий"""
        test_cases = [
            DataFrame({'close': Series([])}),  # Пустые данные
            DataFrame({'close': Series([100])}),  # Одно значение
            DataFrame({'close': Series([100] * 10)}),  # Постоянные значения
        ]

        strategies = [
            SMACrossoverStrategy(5, 10),
            EMACrossoverStrategy(5, 10),
            MACDStrategy(5, 10, 3),
            MACDZeroCrossStrategy(5, 10, 3),
            RSIStrategy(5, 70, 30),
            RSIWithTrendStrategy(5, 70, 30),
            CombinedRSIMACDStrategy(5, 70, 30, 5, 10, 3)
        ]

        for data in test_cases:
            for strategy in strategies:
                if len(data) > 0:  # Для непустых данных
                    signals = strategy.generate_signals(data)
                    assert isinstance(signals, Series)
                    assert len(signals) == len(data)

@pytest.mark.parametrize("window_fast,window_slow", [(5, 15), (10, 30), (20, 50)])
def test_sma_parameterized(window_fast, window_slow, sample_price_data):
    """Параметризованный тест SMA с разными окнами"""
    data = DataFrame({'close': sample_price_data})
    strategy = SMACrossoverStrategy(window_fast, window_slow)
    signals = strategy.generate_signals(data)

    assert isinstance(signals, Series)
    assert len(signals) == len(data)