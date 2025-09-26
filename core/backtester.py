from datetime import datetime
from core.logger import Logger
from core.portfolio import Portfolio
from typing import Dict, Optional, Tuple
from core.order_executor import OrderExecutor
from pandas import DataFrame, Series, to_datetime
from core.metrics_calculator import MetricsCalculator

class Backtester:
    """
    Основной движок бэктестинга торговых стратегий.

    Класс отвечает за проведение полного цикла бэктестинга: от исполнения торговых сигналов
    до расчета метрик производительности и формирования отчетов.

    Аргументы:
        initial_capital (float): Начальный капитал для тестирования
        portfolio (Portfolio): Объект управления портфелем
        order_executor (OrderExecutor): Исполнитель ордеров
        metrics_calculator (MetricsCalculator): Калькулятор метрик
        logger (Logger): Логгер для записи процесса бэктестинга
        results (Dict): Словарь с результатами бэктеста
        equity_curve (Series): Кривая изменения капитала во времени
    """

    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001, slippage: float = 0.001):
        """
        Инициализация движка бэктестинга.

        Аргументы:
            initial_capital (float): Начальный капитал в долларах (по умолчанию 10,000)
            commission (float): Размер комиссии в процентах (по умолчанию 0.1%)
            slippage (float): Размер проскальзывания в процентах (по умолчанию 0.1%)
        """
        self.initial_capital = initial_capital
        self.portfolio = Portfolio(initial_capital)
        self.order_executor = OrderExecutor(commission, slippage)
        self.metrics_calculator = MetricsCalculator()
        self.logger = Logger(__name__)

        self.results: Dict = {}
        self.equity_curve: Optional[Series] = None

        self.logger.info(f"✅ Инициализирован бэктестер с начальным капиталом ${initial_capital:,.2f}")

    def run_backtest(self, data: DataFrame, strategy: type, **strategy_params) -> Dict:
        """
        Запуск полного цикла бэктестинга торговой стратегии.

        Аргументы:
            data (DataFrame): Исторические данные, должены содержать колонки:
                ['open', 'high', 'low', 'close', 'volume'] и опционально 'symbol'
            strategy (type): Класс торговой стратегии
            **strategy_params: Произвольные параметры для передачи в стратегию

        Возвращает:
            Dict: Словарь с полными результатами бэктеста, включая метрики, кривую капитала и историю сделок
                metrics (Dict): Рассчитанные метрики производительности
                equity_curve (Series): Кривая изменения капитала во времени
                trades (List): История всех совершенных сделок
                portfolio_history (List): История изменений портфеля
                final_portfolio_value (float): Конечная стоимость портфеля
                total_trades (int): Общее количество сделок

        Исключения:
            ValueError: Если данные не содержат необходимых колонок
            Exception: При ошибках в процессе бэктестинга

        Пример:
        >>> # Пример использования с классом стратегии
        >>> import pandas as pd
        >>> from datetime import datetime
        >>> i=0
        >>> # Создаем тестовые данные
        >>> dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        >>> backtest_data = pd.DataFrame({
        ...     'open': [100 + i * 0.1 for i in range(len(dates))],
        ...     'high': [101 + i * 0.1 for i in range(len(dates))],
        ...     'low': [99 + i * 0.1 for i in range(len(dates))],
        ...     'close': [100 + i * 0.1 for i in range(len(dates))],
        ...     'volume': [1000000] * len(dates),
        ...     'symbol': ['TEST'] * len(dates)
        ... }, index=dates)
        >>>
        >>> # Класс простой стратегии
        >>> class SimpleStrategy:
        ...     def __init__(self, window=10, threshold=0.5):
        ...         self.window = window
        ...         self.threshold = threshold
        ...
        ...     def generate_signals(self, signals_data):
        ...         backtest_signals = pd.Series(0, index=data.index)
        ...         rolling_mean = backtest_data['close'].rolling(self.window).mean()
        ...         signals_data[backtest_data['close'] > rolling_mean + self.threshold] = 1
        ...         signals_data[backtest_data['close'] < rolling_mean - self.threshold] = -1
        ...         return signals_data
        >>>
        >>> backtester = Backtester(initial_capital=10000)
        >>> results = backtester.run_backtest(data, SimpleStrategy, window=10, threshold=1.0)
        >>> print(f"Конечная стоимость портфеля: ${results['final_portfolio_value']:.2f}")
    """
        self.logger.info("🚀 Запуск бэктестинга...")

        # Валидация входных данных
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            error_msg = f"❌ Отсутствуют необходимые колонки в данных. Требуются: {required_columns}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info(f"📊 Загружено {len(data)} баров данных")
        self.logger.info(f"📅 Период данных: {data.index[0]} - {data.index[-1]}")

        # Создание экземпляра стратегии и генерация сигналов
        self.logger.info("🎯 Генерация торговых сигналов...")
        try:
            strategy_instance = strategy(**strategy_params)
            signals = strategy_instance.generate_signals(data)
            self.logger.info(f"📈 Сгенерировано {len(signals[signals != 0])} торговых сигналов")
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации сигналов стратегии: {e}", info=True)
            raise

        # Симуляция торговли
        self._simulate_trading(data, signals)

        # Расчет результатов
        self.results = self._calculate_results(data)

        self.logger.info("✅ Бэктестинг успешно завершен")
        return self.results

    def _simulate_trading(self, data: DataFrame, signals: Series):
        """
        Симуляция торговли на основе сгенерированных сигналов.
        Проходит по каждому бару данных, проверяет наличие торгового сигнала
        и исполняет соответствующие ордера через OrderExecutor.

        Аргументы:
            data (DataFrame) Исторические цены
            signals (Series) с торговыми сигналами (1 - покупка, -1 - продажа, 0 - бездействие)
        """
        symbol = data['symbol'].iloc[0] if 'symbol' in data.columns else 'UNKNOWN'

        self.logger.info(f"💼 Начало симуляции торговли для символа: {symbol}")

        for i, (timestamp, row) in enumerate(data.iterrows()):
            current_price = row['close']
            signal = signals.iloc[i] if i < len(signals) else 0

            # Пропускаем первые бары для инициализации индикаторов
            if i == 0:
                self.logger.debug("⏭️ Пропуск первого бара для инициализации")
                continue

            # Убеждаемся, что timestamp является datetime
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)

            # Исполнение сигнала
            if signal != 0:
                action = "🟢 Покупку" if signal > 0 else "🔴 Продажа"
                self.logger.debug(f"🎯 Сигнал {action} на баре {i}, цена: ${current_price:.2f}")

                self.order_executor.execute_signal(
                    portfolio=self.portfolio,
                    symbol=symbol,
                    signal=signal,
                    current_price=current_price,
                    timestamp=timestamp,
                    quantity=100,  # Фиксированный размер лота
                    reason=f"Bar {i}"
                )

            # Обновление стоимости портфеля
            current_prices = {symbol: current_price}
            portfolio_value = self.portfolio.update_portfolio_value(current_prices, timestamp)

            # Логируем прогресс каждые 10% данных
            if i % max(1, len(data) // 10) == 0:
                progress = (i / len(data)) * 100
                self.logger.info(f"📊 Прогресс: {progress:.1f}%, Текущая стоимость портфеля: ${portfolio_value:,.2f}")

    def _calculate_results(self, data: DataFrame) -> Dict:
        """
        Расчет всех метрик производительности по завершении бэктеста.

        Аргументы:
            data (DataFrame): Исторические данные

        Возвращает:
            Dict: Полные результаты бэктеста включая метрики, кривую капитала и историю сделок
        """
        self.logger.info("📐 Расчет метрик производительности...")

        # Строим кривую капитала
        equity_curves = self.portfolio.get_equity_curve(data)

        # Основная кривая для метрик - общая стоимость
        self.equity_curve = equity_curves['total']

        # Получаем историю сделок
        trades = self.portfolio.trade_history

        # Расчет метрик
        metrics = self.metrics_calculator.calculate_all_metrics(self.equity_curve, trades)

        # Формирование полных результатов
        results = {
            'trades': trades,
            'metrics': metrics,
            'equity_curves': equity_curves,
            'equity_curve': self.equity_curve,
            'portfolio_history': self.portfolio.portfolio_history,
            'final_portfolio_value': self.equity_curve.iloc[-1] if len(self.equity_curve) > 0 else self.initial_capital,
            'total_trades': len(trades),
            'symbol': data['symbol'].iloc[0] if 'symbol' in data.columns else 'UNKNOWN',
            'initial_capital': self.initial_capital,
            'backtest_period': {'start': data.index[0], 'end': data.index[-1],
                                'days': (data.index[-1] - data.index[0]).days}
        }

        self.logger.info(f"✅ Рассчитано {len(metrics)} метрик, {len(trades)} сделок")
        return results