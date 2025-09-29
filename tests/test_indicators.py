import pytest
import numpy as np
from pandas import Series
from indicators import EMA, SMA, RSI, MACD

class TestEMA:
    """Тесты для экспоненциальной скользящей средней"""

    def test_ema_basic_calculation(self, sample_price_data):
        """Тест базового расчета EMA с использованием fixture"""
        # Arrange
        data = sample_price_data
        window = 3

        # Act
        result = EMA.calculate(data, window)

        # Assert
        assert isinstance(result, Series)
        assert len(result) == len(data)
        assert result.iloc[0] == data.iloc[0]
        assert not np.isnan(result.iloc[2])

    def test_ema_with_trends(self, rising_trend_data, falling_trend_data):
        """Тест EMA с разными трендами из fixture"""
        # Восходящий тренд
        ema_rising = EMA.calculate(rising_trend_data, window=10)
        assert ema_rising.iloc[-1] > ema_rising.iloc[-10]

        # Нисходящий тренд  
        ema_falling = EMA.calculate(falling_trend_data, window=10)
        assert ema_falling.iloc[-1] < ema_falling.iloc[-10]

    def test_ema_volatile_data(self, volatile_data):
        """Тест EMA с волатильными данными"""
        result = EMA.calculate(volatile_data, window=20)
        assert isinstance(result, Series)
        assert len(result) == len(volatile_data)

    def test_ema_constant_series(self):
        """Тест EMA для постоянного ряда"""
        # Arrange
        data = Series([5, 5, 5, 5, 5])
        window = 2

        # Act
        result = EMA.calculate(data, window)

        # Assert
        assert all(abs(result.iloc[i] - 5.0) < 1e-10 for i in range(1, len(result)))

    def test_ema_increasing_series(self):
        """Тест EMA для возрастающего ряда"""
        # Arrange
        data = Series([1, 2, 3, 4, 5])
        window = 3

        # Act
        result = EMA.calculate(data, window)

        # Assert
        # EMA возрастающего ряда должна возрастать
        assert result.iloc[2] < result.iloc[3] < result.iloc[4]

    def test_ema_single_element(self):
        """Тест EMA для ряда с одним элементом"""
        # Arrange
        data = Series([10])
        window = 2

        # Act
        result = EMA.calculate(data, window)

        # Assert
        assert len(result) == 1
        assert result.iloc[0] == 10.0

    def test_ema_window_larger_than_data(self):
        """Тест когда окно больше длины данных"""
        # Arrange
        data = Series([1, 2, 3])
        window = 5

        # Act
        result = EMA.calculate(data, window)

        # Assert
        assert isinstance(result, Series)
        assert len(result) == 3

    @pytest.mark.parametrize("window", [5, 10, 20])
    def test_ema_different_windows(self, sample_price_data, window):
        """Тест EMA с разными размерами окон"""
        result = EMA.calculate(sample_price_data, window)
        assert isinstance(result, Series)
        assert len(result) == len(sample_price_data)

class TestSMA:
    """Тесты для простой скользящей средней"""

    def test_sma_basic_calculation(self, sample_price_data):
        """Тест SMA с fixture"""
        # Arrange
        data = sample_price_data
        window = 3

        # Act
        result = SMA.calculate(data, window)

        # Assert
        assert isinstance(result, Series)
        assert len(result) == len(data)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == (data.iloc[0] + data.iloc[1] + data.iloc[2]) / 3

    def test_sma_trends(self, rising_trend_data):
        """Тест SMA с трендовыми данными"""
        result = SMA.calculate(rising_trend_data, window=10)
        # SMA должна следовать за восходящим трендом
        assert result.iloc[15] < result.iloc[25] < result.iloc[35]

    def test_sma_volatile_data(self, volatile_data):
        """Тест SMA с волатильными данными"""
        result = SMA.calculate(volatile_data, window=20)
        assert isinstance(result, Series)
        assert len(result) == len(volatile_data)

    def test_sma_window_equals_data_length(self):
        """Тест SMA когда окно равно длине данных"""
        # Arrange
        data = Series([10, 20, 30, 40])
        window = 4

        # Act
        result = SMA.calculate(data, window)

        # Assert
        assert result.iloc[3] == 25.0  # (10+20+30+40)/4

    def test_sma_constant_series(self):
        """Тест SMA для постоянного ряда"""
        # Arrange
        data = Series([3, 3, 3, 3, 3])
        window = 3

        # Act
        result = SMA.calculate(data, window)

        # Assert
        assert result.iloc[2] == 3.0
        assert result.iloc[3] == 3.0
        assert result.iloc[4] == 3.0

    def test_sma_single_element(self):
        """Тест SMA для ряда с одним элементом"""
        # Arrange
        data = Series([5])
        window = 1

        # Act
        result = SMA.calculate(data, window)

        # Assert
        assert result.iloc[0] == 5.0

    @pytest.mark.parametrize("window", [3, 5, 10])
    def test_sma_different_windows(self, sample_price_data, window):
        """Тест SMA с разными размерами окон"""
        result = SMA.calculate(sample_price_data, window)
        assert isinstance(result, Series)
        assert len(result) == len(sample_price_data)

class TestRSI:
    """Тесты для индекса относительной силы"""

    def test_rsi_with_volatile_data(self, volatile_data):
        """Тест RSI с волатильными данными из fixture"""
        result = RSI.calculate(volatile_data, window=14)

        assert isinstance(result, Series)
        assert len(result) == len(volatile_data)

        # Проверяем что RSI в допустимом диапазоне
        rsi_valid = result.dropna()
        assert all(0 <= r <= 100 for r in rsi_valid)

    def test_rsi_extreme_cases(self, rising_trend_data, falling_trend_data):
        """Тест RSI с экстремальными трендами"""
        # Сильный восходящий тренд
        rsi_rising = RSI.calculate(rising_trend_data, window=10)
        # При сильном росте RSI должен быть высоким
        assert rsi_rising.iloc[-1] > 60

        # Сильный нисходящий тренд
        rsi_falling = RSI.calculate(falling_trend_data, window=10)
        # При сильном падении RSI должен быть низким
        assert rsi_falling.iloc[-1] < 40

    def test_rsi_basic_calculation(self):
        """Тест базового расчета RSI"""
        # Arrange
        data = Series([44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.86, 46.08])
        window = 6

        # Act
        result = RSI.calculate(data, window)

        # Assert
        assert isinstance(result, Series)
        assert len(result) == len(data)
        # RSI должен быть в диапазоне 0-100
        assert all((0 <= rsi <= 100) or np.isnan(rsi) for rsi in result)

    def test_rsi_all_gains(self):
        """Тест RSI для ряда только с ростами"""
        # Arrange
        data = Series([100, 101, 102, 103, 104, 105])
        window = 3

        # Act
        result = RSI.calculate(data, window)

        # Assert
        # При только растущих ценах RSI должен стремиться к 100
        assert result.iloc[-1] > 90

    def test_rsi_all_losses(self):
        """Тест RSI для ряда только с падениями"""
        # Arrange
        data = Series([105, 104, 103, 102, 101, 100])
        window = 3

        # Act
        result = RSI.calculate(data, window)

        # Assert
        # При только падающих ценах RSI должен стремиться к 0
        assert result.iloc[-1] < 10

    def test_rsi_alternating_prices(self):
        """Тест RSI для чередующихся цен"""
        # Arrange
        data = Series([100, 101, 100, 101, 100, 101])
        window = 2

        # Act
        result = RSI.calculate(data, window)

        # Assert
        # При чередующихся ценах RSI должен быть около 50
        assert 40 <= result.iloc[-1] <= 60

    def test_rsi_window_larger_than_data(self):
        """Тест RSI когда окно больше длины данных"""
        # Arrange
        data = Series([1, 2, 3])
        window = 5

        # Act
        result = RSI.calculate(data, window)

        # Assert
        assert isinstance(result, Series)
        assert len(result) == 3

    @pytest.mark.parametrize("window", [6, 14, 21])
    def test_rsi_different_windows(self, volatile_data, window):
        """Тест RSI с разными периодами"""
        result = RSI.calculate(volatile_data, window)
        assert isinstance(result, Series)
        assert len(result) == len(volatile_data)

class TestMACD:
    """Тесты для индикатора MACD"""

    def test_macd_with_realistic_data(self, volatile_data):
        """Тест MACD с реалистичными данными"""
        macd_line, signal_line, histogram = MACD.calculate(volatile_data)

        assert isinstance(macd_line, Series)
        assert isinstance(signal_line, Series)
        assert isinstance(histogram, Series)
        assert len(macd_line) == len(volatile_data)

    def test_macd_trend_detection(self, rising_trend_data, falling_trend_data):
        """Тест MACD правильно определяет тренды"""
        # Восходящий тренд
        macd_up, _, _ = MACD.calculate(rising_trend_data)
        assert macd_up.iloc[-1] > 0

        # Нисходящий тренд
        macd_down, _, _ = MACD.calculate(falling_trend_data)
        assert macd_down.iloc[-1] < 0

    def test_macd_basic_calculation(self):
        """Тест базового расчета MACD"""
        # Arrange
        data = Series([i * 0.5 + 10 for i in range(50)])  # Восходящий тренд
        fast_window = 12
        slow_window = 26
        signal_window = 9

        # Act
        macd_line, signal_line, histogram = MACD.calculate(
            data, fast_window, slow_window, signal_window
        )

        # Assert
        assert isinstance(macd_line, Series)
        assert isinstance(signal_line, Series)
        assert isinstance(histogram, Series)
        assert len(macd_line) == len(data)
        assert len(signal_line) == len(data)
        assert len(histogram) == len(data)

        # Проверяем, что гистограмма = MACD - Signal
        assert all(
            (histogram[i] == macd_line[i] - signal_line[i])
            or (np.isnan(histogram[i]) and np.isnan(macd_line[i]) and np.isnan(signal_line[i]))
            for i in range(len(data))
        )

    def test_macd_rising_trend(self):
        """Тест MACD для восходящего тренда"""
        # Arrange
        data = Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

        # Act
        macd_line, signal_line, histogram = MACD.calculate(data)

        # Assert
        # При восходящем тренде MACD должен быть положительным
        assert macd_line.iloc[-1] > 0

    def test_macd_falling_trend(self):
        """Тест MACD для нисходящего тренда"""
        # Arrange
        data = Series([20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10])

        # Act
        macd_line, signal_line, histogram = MACD.calculate(data)

        # Assert
        # При нисходящем тренде MACD должен быть отрицательным
        assert macd_line.iloc[-1] < 0

    def test_macd_cross_above_signal(self):
        """Тест когда MACD пересекает сигнальную линию снизу вверх"""
        # Arrange
        # Создаем данные, где сначала падение, затем рост
        data = Series([20, 19, 18, 17, 16, 17, 18, 19, 20, 21, 22])

        # Act
        macd_line, signal_line, histogram = MACD.calculate(data, 3, 6, 2)

        # Assert
        # Должны получить положительную гистограмму в конце
        assert histogram.iloc[-1] > 0

    def test_macd_custom_parameters(self):
        """Тест MACD с пользовательскими параметрами"""
        # Arrange
        data = Series(range(1, 101))
        fast_window = 5
        slow_window = 10
        signal_window = 3

        # Act
        macd_line, signal_line, histogram = MACD.calculate(
            data, fast_window, slow_window, signal_window
        )

        # Assert
        assert isinstance(macd_line, Series)
        assert len(macd_line) == len(data)

    @pytest.mark.parametrize("fast,slow,signal", [
        (12, 26, 9),
        (5, 10, 3),
        (8, 21, 5)
    ])
    def test_macd_different_parameters(self, sample_price_data, fast, slow, signal):
        """Тест MACD с разными параметрами"""
        macd_line, signal_line, histogram = MACD.calculate(
            sample_price_data, fast, slow, signal
        )
        assert isinstance(macd_line, Series)
        assert len(macd_line) == len(sample_price_data)

class TestIntegration:
    """Интеграционные тесты для нескольких индикаторов"""

    def test_all_indicators_together(self, volatile_data):
        """Тест всех индикаторов на одних данных"""
        # Act - рассчитываем все индикаторы
        ema = EMA.calculate(volatile_data, window=20)
        sma = SMA.calculate(volatile_data, window=20)
        rsi = RSI.calculate(volatile_data, window=14)
        macd_line, signal_line, histogram = MACD.calculate(volatile_data)

        # Assert - проверяем корректность всех результатов
        indicators = [ema, sma, rsi, macd_line, signal_line, histogram]
        for indicator in indicators:
            assert isinstance(indicator, Series)
            assert len(indicator) == len(volatile_data)

        # Дополнительные проверки
        assert all(0 <= r <= 100 or np.isnan(r) for r in rsi)
        # Проверяем соотношение гистограммы
        valid_indices = ~np.isnan(histogram) & ~np.isnan(macd_line) & ~np.isnan(signal_line)
        assert all(
            histogram[i] == macd_line[i] - signal_line[i]
            for i in range(len(histogram))
            if valid_indices[i]
        )

    def test_indicators_with_different_data_types(self, sample_price_data, rising_trend_data, volatile_data):
        """Тест индикаторов с разными типами данных"""
        datasets = [sample_price_data, rising_trend_data, volatile_data]

        for data in datasets:
            # Проверяем что все индикаторы работают с каждым типом данных
            ema = EMA.calculate(data, 10)
            sma = SMA.calculate(data, 10)
            rsi = RSI.calculate(data, 14)
            macd_line, signal_line, histogram = MACD.calculate(data)

            # Базовые проверки
            for indicator in [ema, sma, rsi, macd_line, signal_line, histogram]:
                assert isinstance(indicator, Series)
                assert len(indicator) == len(data)

    def test_edge_cases(self):
        """Тест пограничных случаев для всех индикаторов"""
        # Arrange
        empty_series = Series([], dtype=float)
        single_value = Series([100])
        constant_series = Series([50] * 10)

        # Act & Assert - проверяем что функции не падают
        for data in [empty_series, single_value, constant_series]:
            # EMA
            ema_result = EMA.calculate(data, 5)
            assert isinstance(ema_result, Series)

            # SMA
            sma_result = SMA.calculate(data, 5)
            assert isinstance(sma_result, Series)

            # RSI
            rsi_result = RSI.calculate(data, 5)
            assert isinstance(rsi_result, Series)

            # MACD
            if len(data) > 0:  # MACD требует хотя бы одно значение
                macd_line, signal_line, histogram = MACD.calculate(data, 3, 5, 2)
                assert isinstance(macd_line, Series)
                assert isinstance(signal_line, Series)
                assert isinstance(histogram, Series)