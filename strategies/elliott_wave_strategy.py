from enum import Enum, auto
from dataclasses import dataclass
from strategies import BaseStrategy
from pandas import DataFrame, Series
from indicators import EMA, RSI, MACD
from typing import Dict, List, Optional, Tuple

class TrendState(Enum):
    """
    Состояния тренда рынка.

    Атрибуты:
        NEUTRAL: Боковой тренд, неопределенность
        BULLISH: Бычий тренд, движение вверх
        BEARISH: Медвежий тренд, движение вниз
    """
    NEUTRAL = auto()
    BULLISH = auto()
    BEARISH = auto()

class WaveType(Enum):
    """
    Типы волн Эллиотта.

    Импульсные волны (по тренду):
        WAVE_1: Начало движения, слабая уверенность
        WAVE_3: Самая сильная волна, максимальный объем
        WAVE_5: Завершение тренда, дивергенции

    Коррекционные волны (против тренда):
        WAVE_2: Откат после волны 1, обычно 50-61.8%
        WAVE_4: Консолидация перед финальным движением

    Коррекционные паттерны (A-B-C):
        WAVE_A: Начало коррекции
        WAVE_B: Откат внутри коррекции
        WAVE_C: Завершение коррекционной структуры
    """
    WAVE_1 = "Wave 1"
    WAVE_2 = "Wave 2"
    WAVE_3 = "Wave 3"
    WAVE_4 = "Wave 4"
    WAVE_5 = "Wave 5"
    WAVE_A = "Wave A"
    WAVE_B = "Wave B"
    WAVE_C = "Wave C"
    UNKNOWN = "Unknown"
    COMPLETED = "Completed"

class ExtremeType(Enum):
    """
    Типы экстремумов цен.

    Атрибуты:
        HIGH: Локальный максимум (свинг-хай)
        LOW: Локальный минимум (свинг-лоу)
        NONE: Отсутствие экстремума
    """
    HIGH = "high"
    LOW = "low"
    NONE = "none"

class CorrectionPattern(Enum):
    """
    Типы коррекционных паттернов.

    Атрибуты:
        ZIGZAG: Резкая коррекция 5-3-5
        FLAT: Горизонтальная коррекция 3-3-5
        TRIANGLE: Сужение диапазона 3-3-3-3-3
        COMBINATION: Комбинированные коррекции
    """
    ZIGZAG = "ZigZag"
    FLAT = "Flat"
    TRIANGLE = "Triangle"
    COMBINATION = "Combination"
    UNKNOWN = "Unknown"

@dataclass
class WavePoint:
    """
    Точка волны с метаданными для анализа.

    Атрибуты:
        index (int): Индекс в DataFrame
        price (float): Цена экстремума
        wave_type (WaveType): Тип волны Эллиотта
        extreme_type (ExtremeType): Тип экстремума
        timestamp (any): Временная метка
        confidence (float): Уверенность в разметке (0-1)
        volume (float): Объем в точке экстремума
    """
    index: int
    price: float
    wave_type: WaveType
    extreme_type: ExtremeType
    timestamp: any
    confidence: float = 0.0
    volume: float = 0.0

@dataclass
class WaveStructure:
    """
    Полная волновая структура для анализа.

    Атрибуты:
        points (List[WavePoint]): Список точек волновой структуры
        trend (TrendState): Преобладающий тренд
        is_valid (bool): Валидность структуры по правилам Эллиотта
        completion_ratio (float): Степень завершенности (0-1)
        fibonacci_ratios (Dict[str, float]): Соотношения Фибоначчи между волнами
        pattern_type (CorrectionPattern): Тип коррекционного паттерна
        start_time (any): Время начала структуры
        end_time (any): Время завершения структуры
    """
    points: List[WavePoint]
    trend: TrendState
    is_valid: bool
    completion_ratio: float
    fibonacci_ratios: Dict[str, float]
    pattern_type: CorrectionPattern = CorrectionPattern.UNKNOWN
    start_time: any = None
    end_time: any = None

@dataclass
class TradingSignal:
    """
    Торговый сигнал с метаданными.

    Атрибуты:
        timestamp: Временная метка сигнала
        signal: Направление сигнала (1 - покупка, -1 - продажа)
        price: Цена в момент сигнала
        wave_type: Тип волны, сгенерировавшей сигнал
        confidence: Уверенность в сигнале (0-1)
        stop_loss: Уровень стоп-lost
        targets: Список ценовых целей
        risk_reward: Соотношение риск/прибыль
    """
    timestamp: any
    signal: int
    price: float
    wave_type: WaveType
    confidence: float
    stop_loss: float
    targets: List[float]
    risk_reward: float

class ElliottWaveStrategy(BaseStrategy):
    """
    Стратегия волн Эллиотта с фильтрацией RSI/MACD/EMA.
    Сочетает точность волнового анализа с надежностью технических индикаторов.
    Эффективна на трендовых рынках с четкими волновыми структурами.
    """

    def __init__(self,
                 rsi_period: int = 14,
                 rsi_overbought: int = 70,
                 rsi_oversold: int = 30,
                 macd_fast: int = 12,
                 macd_slow: int = 26,
                 macd_signal: int = 9,
                 ema_fast: int = 9,
                 ema_slow: int = 21,
                 swing_window: int = 5,
                 min_wave_ratio: float = 0.382,
                 max_wave_ratio: float = 2.618,
                 confidence_threshold: float = 0.7,
                 risk_reward_ratio: float = 1.5,
                 use_rsi_filter: bool = True,
                 use_macd_filter: bool = True,
                 use_ema_filter: bool = True):
        """
        Инициализация стратегии волн Эллиотта.

        Аргументы:
            rsi_period (int, optional): Период расчета RSI (по умолчанию 14)
            rsi_overbought (int, optional): Уровень перекупленности (по умолчанию 70)
            rsi_oversold (int, optional): Уровень перепроданности (по умолчанию 30)
            macd_fast (int, optional): Быстрый период MACD (по умолчанию 12)
            macd_slow (int, optional): Медленный период MACD (по умолчанию 26)
            macd_signal (int, optional): Сигнальный период MACD (по умолчанию 9)
            ema_fast (int, optional): Период быстрой EMA (по умолчанию 9)
            ema_slow (int, optional): Период медленной EMA (по умолчанию 21)
            swing_window (int, optional): Окно для поиска свинг-точек (по умолчанию 5)
            min_wave_ratio (float, optional): Минимальное соотношение волн (по умолчанию 0.382)
            max_wave_ratio (float, optional): Максимальное соотношение волн (по умолчанию 2.618)
            confidence_threshold (float, optional): Порог уверенности для сигналов (по умолчанию 0.7)
            risk_reward_ratio (float, optional): Минимальное соотношение риск/прибыль (по умолчанию 1.5)
            use_rsi_filter (bool, optional): Использовать RSI фильтр (по умолчанию True)
            use_macd_filter (bool, optional): Использовать MACD фильтр (по умолчанию True)
            use_ema_filter (bool, optional): Использовать EMA фильтр (по умолчанию True)

        Применение:
            Для дневных таймфреймов: классические настройки
            Для часовых: уменьшить периоды индикаторов (RSI 10, EMA 7/14)
            Для недельных: увеличить периоды индикаторов (RSI 21, EMA 14/28)
        """
        # Параметры индикаторов
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.swing_window = swing_window

        # Параметры валидации
        self.min_wave_ratio = min_wave_ratio
        self.max_wave_ratio = max_wave_ratio
        self.confidence_threshold = confidence_threshold
        self.risk_reward_ratio = risk_reward_ratio

        # Фильтры
        self.use_rsi_filter = use_rsi_filter
        self.use_macd_filter = use_macd_filter
        self.use_ema_filter = use_ema_filter

        # Кэширование для производительности
        self._cached_indicators: Dict[str, Series] = {}
        self._cached_swing_points: Optional[Tuple[Series, Series]] = None

    def generate_signals(self, data: DataFrame) -> Series:
        """
        Генерация торговых сигналов на основе волнового анализа и индикаторов.

        Аргументы:
            data (DataFrame): Данные с ценами, должен содержать колонку 'close'

        Возвращает:
            Series: Торговые сигналы: 1 (BUY), -1 (SELL), 0 (HOLD)

        Стратегия:
            🟢 Покупка: Завершение коррекционной волны 2/4 + RSI перепродан + MACD/EMA бычьи
            🔴 Продажа: Завершение коррекционной волны 2/4 + RSI перекуплен + MACD/EMA медвежьи
            ➡️ Держать: В остальных случаях

        Пример:
        >>> prices = DataFrame([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> strategy = ElliottWaveStrategy()
        >>> signals = strategy.generate_signals(prices)
        """
        if len(data) < self._get_min_required_bars():
            return Series(0, index=data.index)

        # Предварительный расчет индикаторов
        self._precalculate_indicators(data)

        # Генерация расширенных сигналов
        advanced_signals = self._generate_advanced_signals(data)

        # Конвертация в простой формат
        return self._convert_to_simple_signals(advanced_signals, data.index)

    def _get_min_required_bars(self) -> int:
        """
        Расчет минимального количества баров для анализа.

        Возвращает:
            int: Минимальное количество баров
        """
        return max(self.ema_slow, self.macd_slow, self.swing_window * 2) + 10

    def _precalculate_indicators(self, data: DataFrame) -> None:
        """
        Предварительный расчет индикаторов для оптимизации производительности.

        Аргументы:
            data (DataFrame): Данные для расчета индикаторов
        """
        self._cached_indicators = {
            'rsi': RSI.calculate(data['close'], self.rsi_period),
            'ema_fast': EMA.calculate(data['close'], self.ema_fast),
            'ema_slow': EMA.calculate(data['close'], self.ema_slow),
            'macd_line': MACD.calculate(data['close'], self.macd_fast, self.macd_slow, self.macd_signal)[0],
            'macd_signal': MACD.calculate(data['close'], self.macd_fast, self.macd_slow, self.macd_signal)[1]
        }

        # Кэширование свинг-точек
        self._cached_swing_points = self._detect_swing_points(data['close'], self.swing_window)

    def _generate_advanced_signals(self, data: DataFrame) -> List[TradingSignal]:
        """
        Генерация расширенных торговых сигналов с метаданными.

        Аргументы:
            data (DataFrame): Данные с рыночными данными

        Возвращает:
            List[TradingSignal]: Список торговых сигналов
        """
        signals = []
        start_index = self._get_min_required_bars()

        for i in range(start_index, len(data)):
            signal = self._analyze_single_bar(data, i)
            if signal and signal.confidence >= self.confidence_threshold:
                signals.append(signal)

        return signals

    def _analyze_single_bar(self, data: DataFrame, index: int) -> Optional[TradingSignal]:
        """
        Анализ одного бара для генерации сигнала.

        Аргументы:
            data (DataFrame): Полный набор данных
            index (int): Индекс анализируемого бара

        Возвращает:
            Optional[TradingSignal]: Торговый сигнал или None
        """
        current_data = data.iloc[:index + 1]

        # Быстрая проверка на наличие экстремумов
        if not self._has_recent_extremes(index):
            return None

        # Анализ волновой структуры
        structure = self._analyze_current_wave_structure(current_data, index)
        if not structure or not structure.is_valid:
            return None

        # Генерация сигнала
        return self._generate_trading_signal(structure, data.iloc[index], index)

    def _has_recent_extremes(self, index: int, lookback: int = 20) -> bool:
        """
        Проверка наличия недавних экстремумов.

        Аргументы:
            index (int): Текущий индекс для проверки
            lookback (int, optional): Количество баров для поиска назад (по умолчанию 20)

        Возвращает:
            bool: True если найдены экстремумы
        """
        if self._cached_swing_points is None:
            return False

        swing_highs, swing_lows = self._cached_swing_points
        start_idx = max(0, index - lookback)

        recent_highs = swing_highs.iloc[start_idx:index + 1].sum()
        recent_lows = swing_lows.iloc[start_idx:index + 1].sum()

        return recent_highs > 0 or recent_lows > 0

    def _generate_trading_signal(self, structure: WaveStructure, current_bar, index: int) -> Optional[TradingSignal]:
        """
        Генерация торгового сигнала на основе волновой структуры.

        Аргументы:
            structure (WaveStructure): Проанализированная волновая структура
            current_bar: Текущий бар данных
            index (int): Индекс текущего бара

        Возвращает:
            Optional[TradingSignal]: Сформированный торговый сигнал
        """
        last_wave = structure.points[-1]
        current_price = current_bar['close']

        # Получение значений индикаторов
        indicator_values = self._get_indicator_values(index)
        if indicator_values is None:
            return None

        # Генерация базового сигнала
        base_signal = self._generate_base_signal(structure, last_wave)
        if base_signal == 0:
            return None

        # Применение фильтров
        filters_passed = self._apply_technical_filters(base_signal, *indicator_values)
        if not filters_passed:
            return None

        # Расчет целей и стоп-lost
        stop_loss = self._calculate_stop_loss(structure, base_signal)
        targets = self._calculate_targets(structure, current_price, base_signal)
        risk_reward = self._calculate_risk_reward(current_price, targets[0], stop_loss)

        if risk_reward < self.risk_reward_ratio:
            return None

        # Расчет уверенности
        confidence = self._calculate_signal_confidence(structure, indicator_values)

        return TradingSignal(
            timestamp=current_bar.name,
            signal=base_signal,
            price=current_price,
            wave_type=last_wave.wave_type,
            confidence=confidence,
            stop_loss=stop_loss,
            targets=targets,
            risk_reward=risk_reward
        )

    @staticmethod
    def _generate_base_signal(structure: WaveStructure, last_wave: WavePoint) -> int:
        """
        Генерация базового сигнала по типу волны и тренду.

        Аргументы:
            structure (WaveStructure): Волновая структура
            last_wave (WavePoint): Последняя идентифицированная волна

        Возвращает:
            int: 1 (BUY), -1 (SELL), или 0 (нет сигнала)
        """
        if structure.trend == TrendState.BULLISH:
            if last_wave.wave_type in [WaveType.WAVE_2, WaveType.WAVE_4]:
                return 1
        elif structure.trend == TrendState.BEARISH:
            if last_wave.wave_type in [WaveType.WAVE_2, WaveType.WAVE_4]:
                return -1
        return 0

    def _get_indicator_values(self, index: int) -> Optional[Tuple]:
        """
        Получение значений индикаторов для указанного индекса.

        Аргументы:
            index (int): Индекс для получения значений

        Возвращает:
            Optional[Tuple]: Кортеж значений индикаторов
        """
        try:
            return (
                self._cached_indicators['rsi'].iloc[index],
                self._cached_indicators['macd_line'].iloc[index],
                self._cached_indicators['macd_signal'].iloc[index],
                self._cached_indicators['ema_fast'].iloc[index],
                self._cached_indicators['ema_slow'].iloc[index]
            )
        except (KeyError, IndexError):
            return None

    def _calculate_signal_confidence(self, structure: WaveStructure, indicator_values: Tuple) -> float:
        """
        Расчет общей уверенности сигнала.

        Аргументы:
            structure (WaveStructure): Волновая структура
            indicator_values (Tuple): Значения технических индикаторов

        Возвращает:
            float: Общая уверенность сигнала от 0.0 до 1.0
        """
        wave_confidence = structure.completion_ratio

        # Распаковываем значения индикаторов
        rsi, macd_line, macd_signal, ema_fast, ema_slow = indicator_values

        # Передаем тренд как отдельный аргумент
        indicator_confidence = self._calculate_indicator_confidence(
            rsi, macd_line, macd_signal, ema_fast, ema_slow, structure.trend
        )

        return min(1.0, wave_confidence * indicator_confidence)

    @staticmethod
    def _calculate_targets(structure: WaveStructure, current_price: float, signal: int) -> List[float]:
        """
        Расчет ценовых целей на основе волновой структуры.

        Аргументы:
            structure (WaveStructure): Волновая структура
            current_price (float): Текущая цена
            signal (int): Направление сигнала (1 или -1)

        Возвращает:
            List[float]: Список ценовых целей
        """
        if len(structure.points) < 2:
            multiplier = 1.05 if signal == 1 else 0.95
            return [current_price * multiplier, current_price * (multiplier ** 2)]

        wave_1_length = abs(structure.points[1].price - structure.points[0].price)

        if signal == 1:  # BUY
            target_1 = current_price + wave_1_length * 1.618
            target_2 = current_price + wave_1_length * 2.618
        else:  # SELL
            target_1 = current_price - wave_1_length * 1.618
            target_2 = current_price - wave_1_length * 2.618

        return [target_1, target_2]

    @staticmethod
    def _calculate_stop_loss(structure: WaveStructure, signal: int) -> float:
        """
        Расчет уровня стоп-lost.

        Аргументы:
            structure (WaveStructure): Волновая структура
            signal (int): Направление сигнала

        Возвращает:
            float: Уровень стоп-lost
        """
        if not structure.points:
            return 0.0

        last_extreme = structure.points[-1].price
        if signal == 1:  # BUY
            return last_extreme * 0.98
        else:  # SELL
            return last_extreme * 1.02

    def _convert_to_simple_signals(self, advanced_signals: List[TradingSignal], index: Series) -> Series:
        """
        Конвертация расширенных сигналов в простой формат.

        Аргументы:
            advanced_signals (List[TradingSignal]): Список расширенных сигналов
            index (Series): Временной индекс для Series

        Возвращает:
            Series: Упрощенные торговые сигналы
        """
        signals = Series(0, index=index)

        for adv_signal in advanced_signals:
            signals.loc[adv_signal.timestamp] = adv_signal.signal

        return self._filter_consecutive_signals(signals)

    @staticmethod
    def _filter_consecutive_signals(signals: Series) -> Series:
        """
        Фильтрация последовательных сигналов.

        Аргументы:
            signals (Series): Исходные торговые сигналы

        Возвращает:
            Series: Отфильтрованные сигналы без повторов
        """
        filtered_signals = signals.copy()
        last_signal = 0
        last_index = -float('inf')
        min_distance = 5

        for i, current_signal in enumerate(signals):
            if current_signal != 0:
                same_direction = current_signal == last_signal
                sufficient_distance = (i - last_index) >= min_distance

                if not same_direction or sufficient_distance:
                    last_signal = current_signal
                    last_index = i
                else:
                    filtered_signals.iloc[i] = 0

        return filtered_signals

    def _apply_technical_filters(self, wave_signal: int, rsi: float, macd_line: float, macd_signal: float,
                                 ema_fast: float, ema_slow: float) -> bool:
        """
        Применение технических фильтров к волновым сигналам.

        Аргументы:
            wave_signal (int): Базовый волновой сигнал
            rsi (float): Значение RSI
            macd_line (float): Значение линии MACD
            macd_signal (float): Значение сигнальной линии MACD
            ema_fast (float): Значение быстрой EMA
            ema_slow (float): Значение медленной EMA

        Возвращает:
            bool: True если сигнал прошел фильтры
        """
        if wave_signal == 0:
            return False

        filters_passed = 0
        total_filters = 0

        # RSI фильтр
        if self.use_rsi_filter:
            total_filters += 1
            if (wave_signal == 1 and rsi < self.rsi_oversold) or \
                    (wave_signal == -1 and rsi > self.rsi_overbought):
                filters_passed += 1

        # MACD фильтр
        if self.use_macd_filter:
            total_filters += 1
            if (wave_signal == 1 and macd_line > macd_signal) or \
                    (wave_signal == -1 and macd_line < macd_signal):
                filters_passed += 1

        # EMA фильтр
        if self.use_ema_filter:
            total_filters += 1
            if (wave_signal == 1 and ema_fast > ema_slow) or \
                    (wave_signal == -1 and ema_fast < ema_slow):
                filters_passed += 1

        # Прошли как минимум 2/3 фильтров
        return filters_passed >= 2

    def _calculate_indicator_confidence(self, rsi: float, macd_line: float, macd_signal: float, ema_fast: float,
                                        ema_slow: float, trend: TrendState) -> float:
        """
        Расчет уверенности на основе совпадения индикаторов с трендом.

        Аргументы:
            rsi (float): Значение RSI
            macd_line (float): Значение линии MACD
            macd_signal (float): Значение сигнальной линии MACD
            ema_fast (float): Значение быстрой EMA
            ema_slow (float): Значение медленной EMA
            trend (TrendState): Текущий тренд

        Возвращает:
            float: Уверенность от 0.0 до 1.0
        """
        confidences = []

        # RSI уверенность
        if self.use_rsi_filter:
            if trend == TrendState.BULLISH:
                rsi_conf = max(0.0, 1.0 - (rsi / self.rsi_oversold)) if rsi < self.rsi_oversold else 0.0
            else:  # BEARISH
                rsi_conf = max(0.0, (rsi - self.rsi_overbought) / (100 - self.rsi_overbought))
            confidences.append(rsi_conf)

        # MACD уверенность
        if self.use_macd_filter:
            macd_diff = macd_line - macd_signal
            if (trend == TrendState.BULLISH and macd_diff > 0) or (trend == TrendState.BEARISH and macd_diff < 0):
                macd_conf = min(1.0, abs(macd_diff) * 5.0)
                confidences.append(macd_conf)
            else:
                confidences.append(0.0)

        # EMA уверенность
        if self.use_ema_filter:
            ema_diff = (ema_fast - ema_slow) / ema_slow
            if (trend == TrendState.BULLISH and ema_fast > ema_slow) or \
                    (trend == TrendState.BEARISH and ema_fast < ema_slow):
                ema_conf = min(1.0, abs(ema_diff) * 100.0)
                confidences.append(ema_conf)
            else:
                confidences.append(0.0)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def _analyze_current_wave_structure(self, data: DataFrame, current_index: int) -> Optional[WaveStructure]:
        """
        Анализ текущей волновой структуры на основе экстремумов.

        Аргументы:
            data (DataFrame): Данные для анализа
            current_index (int): Текущий индекс анализа

        Возвращает:
            Optional[WaveStructure]: Проанализированная волновая структура
        """
        if self._cached_swing_points is None:
            return None

        swing_highs, swing_lows = self._cached_swing_points
        current_highs = swing_highs.iloc[:current_index + 1]
        current_lows = swing_lows.iloc[:current_index + 1]

        extremes = self._get_ordered_extremes(current_highs, current_lows, data['close'])

        if len(extremes) < 3:
            return None

        trend = self._determine_trend_from_extremes(extremes)
        wave_points = self._identify_wave_points(extremes, trend)

        if len(wave_points) >= 3:
            is_valid, confidence = self._validate_impulse_rules(wave_points)
            fib_ratios = self._calculate_wave_fibonacci_ratios(wave_points)

            return WaveStructure(points=wave_points, trend=trend, is_valid=is_valid,
                                 completion_ratio=len(wave_points) / 5.0, fibonacci_ratios=fib_ratios)
        return None

    @staticmethod
    def _get_ordered_extremes(swing_highs: Series, swing_lows: Series, prices: Series) -> List[WavePoint]:
        """
        Создание упорядоченного списка экстремумов.

        Аргументы:
            swing_highs (Series): Свинг-максимумы
            swing_lows (Series): Свинг-минимумы
            prices (Series): Series с ценами

        Возвращает:
            List[WavePoint]: Упорядоченный список точек экстремумов
        """
        extremes = []

        for idx in swing_highs[swing_highs].index:
            extremes.append(WavePoint(
                index=idx, price=prices.loc[idx], wave_type=WaveType.UNKNOWN,
                extreme_type=ExtremeType.HIGH, timestamp=idx
            ))

        for idx in swing_lows[swing_lows].index:
            extremes.append(WavePoint(
                index=idx, price=prices.loc[idx], wave_type=WaveType.UNKNOWN,
                extreme_type=ExtremeType.LOW, timestamp=idx
            ))

        extremes.sort(key=lambda x: x.index)
        return extremes

    @staticmethod
    def _determine_trend_from_extremes(extremes: List[WavePoint]) -> TrendState:
        """
        Определение тренда на основе последовательности экстремумов.

        Аргументы:
            extremes (List[WavePoint]): Список экстремумов

        Возвращает:
            TrendState: Определенное состояние тренда
        """
        if len(extremes) < 2:
            return TrendState.NEUTRAL

        rising_highs = 0
        falling_lows = 0

        for i in range(1, len(extremes)):
            if extremes[i].extreme_type == ExtremeType.HIGH:
                if extremes[i].price > extremes[i - 1].price:
                    rising_highs += 1
            else:
                if extremes[i].price < extremes[i - 1].price:
                    falling_lows += 1

        if rising_highs > falling_lows:
            return TrendState.BULLISH
        elif falling_lows > rising_highs:
            return TrendState.BEARISH
        else:
            return TrendState.NEUTRAL

    def _identify_wave_points(self, extremes: List[WavePoint], trend: TrendState) -> List[WavePoint]:
        """
        Идентификация типов волн для каждого экстремума.

        Аргументы:
            extremes (List[WavePoint]): Список экстремумов
            trend (TrendState): Определенный тренд

        Возвращает:
            List[WavePoint]: Список точек с идентифицированными типами волн
        """
        wave_points = []
        for i, point in enumerate(extremes):
            wave_type = self._classify_wave_type(i, trend, extremes)
            point.wave_type = wave_type
            wave_points.append(point)
        return wave_points

    @staticmethod
    def _classify_wave_type(index: int, trend: TrendState, extremes: List[WavePoint]) -> WaveType:
        """
        Классификация типа волны для экстремума.

        Аргументы:
            index (int): Индекс экстремума
            trend (TrendState): Текущий тренд
            extremes (List[WavePoint]): Полный список экстремумов

        Возвращает:
            WaveType: Классифицированный тип волны
        """
        if index >= len(extremes):
            return WaveType.UNKNOWN

        if index == 0:
            return WaveType.WAVE_1 if trend == TrendState.BULLISH else WaveType.WAVE_A

        # Анализ соотношений для точной классификации
        if index >= 1:
            current_point = extremes[index]
            prev_point = extremes[index - 1]

            # Расчет отката (только для коррекционных волн)
            if index >= 2 and index % 2 == 1:  # Коррекционные волны (2, 4, B)
                wave_1_length = abs(extremes[1].price - extremes[0].price)
                correction_length = abs(current_point.price - prev_point.price)

                if wave_1_length > 0:
                    retracement_ratio = correction_length / wave_1_length

                    # Волна 2 обычно откатывает 50-61.8%
                    if 0.382 <= retracement_ratio <= 0.786 and index == 1:
                        return WaveType.WAVE_2 if trend == TrendState.BULLISH else WaveType.WAVE_B
                    # Волна 4 обычно откатывает 38.2-50%
                    elif 0.236 <= retracement_ratio <= 0.618 and index == 3:
                        return WaveType.WAVE_4 if trend == TrendState.BULLISH else WaveType.WAVE_A

        # Резервная классификация по индексу
        wave_mapping = {
            0: (WaveType.WAVE_1, WaveType.WAVE_A),
            1: (WaveType.WAVE_2, WaveType.WAVE_B),
            2: (WaveType.WAVE_3, WaveType.WAVE_C),
            3: (WaveType.WAVE_4, WaveType.WAVE_A),
            4: (WaveType.WAVE_5, WaveType.WAVE_B)
        }

        if index in wave_mapping:
            return wave_mapping[index][0] if trend == TrendState.BULLISH else wave_mapping[index][1]

        return WaveType.UNKNOWN

    @staticmethod
    def _validate_impulse_rules(points: List[WavePoint]) -> Tuple[bool, float]:
        """
        Валидация волновой структуры по правилам Эллиотта.

        Аргументы:
            points (List[WavePoint]): Точки волновой структуры

        Возвращает:
            Tuple[bool, float]: (Валидность структуры, Уверенность в валидности)
        """
        if len(points) < 3:
            return False, 0.0

        confidence = 0.0
        rules_passed = 0
        total_rules = 4

        try:
            # Правило 1: Волна 2 не откатывает более 100% волны 1
            if len(points) >= 3:
                wave_1_len = abs(points[1].price - points[0].price)
                wave_2_retrace = abs(points[2].price - points[1].price)

                if wave_1_len > 0:
                    retrace_ratio = wave_2_retrace / wave_1_len
                    if retrace_ratio < 1.0:
                        rules_passed += 1
                        confidence += max(0.0, 1.0 - retrace_ratio)

            # Правило 2: Волна 3 не самая короткая
            if len(points) >= 5:
                wave_3_len = abs(points[3].price - points[2].price)
                wave_1_len = abs(points[1].price - points[0].price)
                wave_5_len = abs(points[4].price - points[3].price)

                if wave_3_len > min(wave_1_len, wave_5_len):
                    rules_passed += 1
                    confidence += 0.25

            # Правило 3: Волна 4 не заходит на территорию волны 1
            if len(points) >= 5:
                if (points[0].extreme_type == ExtremeType.LOW and points[3].price > points[0].price) or \
                        (points[0].extreme_type == ExtremeType.HIGH and points[3].price < points[0].price):
                    rules_passed += 1
                    confidence += 0.25

            # Правило 4: Последовательность экстремумов чередуется
            if len(points) >= 3:
                alternation_valid = True
                for i in range(1, len(points)):
                    if points[i].extreme_type == points[i - 1].extreme_type:
                        alternation_valid = False
                        break

                if alternation_valid:
                    rules_passed += 1
                    confidence += 0.25

        except (IndexError, AttributeError, ZeroDivisionError):
            return False, 0.0

        final_confidence = confidence / float(total_rules) if total_rules > 0 else 0.0
        is_valid = rules_passed >= 2
        return is_valid, final_confidence

    @staticmethod
    def _calculate_wave_fibonacci_ratios(points: List[WavePoint]) -> Dict[str, float]:
        """
        Расчет соотношений Фибоначчи между волнами.

        Аргументы:
            points (List[WavePoint]): Точки волновой структуры

        Возвращает:
            Dict[str, float]: Словарь с соотношениями Фибоначчи
        """
        ratios = {}
        if len(points) >= 5:
            w1, w2, w3, w4, w5 = points[:5]
            len_1 = abs(w2.price - w1.price)
            len_3 = abs(w4.price - w3.price)
            len_5 = abs(w5.price - w4.price)

            if len_1 > 0:
                ratios['W3/W1'] = len_3 / len_1
                ratios['W5/W1'] = len_5 / len_1
            if len_3 > 0:
                ratios['W5/W3'] = len_5 / len_3
            if len_1 > 0:
                ratios['W2/W1'] = abs(w3.price - w2.price) / len_1
            if len_3 > 0:
                ratios['W4/W3'] = abs(w5.price - w4.price) / len_3
        return ratios

    @staticmethod
    def _detect_swing_points(prices: Series, window: int = 5) -> Tuple[Series, Series]:
        """
        Обнаружение свинг-точек (локальных экстремумов).

        Аргументы:
            prices (Series): Series с ценами
            window (int, optional): Окно для поиска экстремумов (по умолчанию 5)

        Возвращает:
            Tuple[Series, Series]: (Свинг-максимумы, Свинг-минимумы)
        """
        if len(prices) < window * 2 + 1:
            return Series(False, index=prices.index), Series(False, index=prices.index)

        highs = Series(False, index=prices.index)
        lows = Series(False, index=prices.index)

        for i in range(window, len(prices) - window):
            current_price = prices.iloc[i]
            left_window = prices.iloc[i - window:i]
            right_window = prices.iloc[i + 1:i + window + 1]

            # Проверка на свинг-хай
            is_high = (current_price > left_window.max() and
                       current_price > right_window.max())

            # Проверка на свинг-лоу
            is_low = (current_price < left_window.min() and
                      current_price < right_window.min())

            highs.iloc[i] = is_high
            lows.iloc[i] = is_low

        return highs, lows

    @staticmethod
    def _calculate_risk_reward(entry_price: float, target: float, stop_loss: float) -> float:
        """
        Расчет соотношения риск/прибыль.

        Аргументы:
            entry_price (float): Цена входа
            target (float): Целевая цена
            stop_loss (float): Цена стоп-lost

        Возвращает:
            float: Соотношение риск/прибыль
        """
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0

        if entry_price > target:
            potential_profit = entry_price - target
            potential_loss = stop_loss - entry_price
        else:
            potential_profit = target - entry_price
            potential_loss = entry_price - stop_loss

        return potential_profit / potential_loss if potential_loss > 0 else 0.0