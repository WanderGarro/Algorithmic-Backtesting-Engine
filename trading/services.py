from core import Backtester
from data import YahooFinanceProvider
from strategies import (SMACrossoverStrategy, RSIStrategy, EMACrossoverStrategy, CombinedRSIMACDStrategy, MACDStrategy,
                        MACDZeroCrossStrategy, RSIWithTrendStrategy)

class TradingService:
    """
    Сервис для управления торговыми операциями и бэктестинга стратегий.
    Класс предоставляет унифицированный интерфейс для запуска бэктестов различных
    торговых стратегий, валидации параметров и получения информации о доступных стратегиях.

    Основные возможности:
    - Запуск бэктеста с различными стратегиями и параметрами
    - Получение списка доступных стратегий с описанием параметров
    - Валидация параметров стратегий перед выполнением
    - Управление настройками комиссий и проскальзывания

    Атрибуты:
        data_provider (DataProvider): Провайдер данных для получения исторических цен
        available_strategies (dict): Словарь с описанием всех доступных стратегий

    Пример использования:
        >>> service = TradingService()
        >>> results = service.run_backtest(
        ...     symbol='AAPL',
        ...     strategy_name='sma_crossover',
        ...     start_date='2023-01-01',
        ...     end_date='2023-12-31',
        ...     initial_capital=10000,
        ...     short_window=20,
        ...     long_window=50
        ... )
    """

    def __init__(self):
        """
        Инициализация торгового сервиса.
        Создает экземпляр провайдера данных для получения исторических цен
        и инициализирует список доступных торговых стратегий.

        Инициализирует:
            data_provider (YahooFinanceProvider): Провайдер для загрузки рыночных данных
            available_strategies (dict): Словарь с метаданными доступных стратегий

        Пример:
            >>> # Создание экземпляра торгового сервиса
            >>> trading_service = TradingService()
            >>> print(f"Доступно стратегий: {len(trading_service.get_available_strategies())}")
            Доступно стратегий: 7
        """
        self.data_provider = YahooFinanceProvider()

    def run_backtest(self, symbol: str, strategy_name: str, start_date: str, end_date: str, initial_capital: float,
                     interval: str = '1d', commission: float = 0.001, slippage: float = 0.001, **strategy_params):
        """
        Запуск полного цикла бэктестинга для указанной стратегии и символа.

        Аргументы:
            symbol (str): Тикер акции (например, 'AAPL', 'GOOGL')
            strategy_name (str): Название стратегии из доступного списка
            start_date (str): Начальная дата периода тестирования в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата периода тестирования в формате 'YYYY-MM-DD'
            initial_capital (float): Начальный капитал для тестирования в долларах
            interval (str, optional): Интервал данных ('1d' - дневной, '1h' - часовой и т.д.)
            commission (float, optional): Размер комиссии в процентах от объема сделки (по умолчанию 0.1%)
            slippage (float, optional): Размер проскальзывания в процентах (по умолчанию 0.1%)
            **strategy_params: Произвольные параметры для передачи в стратегию

        Возвращает:
            Dict: Полные результаты бэктеста включая:
                metrics (Dict): Рассчитанные метрики производительности
                equity_curve (Series): Кривая изменения капитала во времени
                trades (List): История всех совершенных сделок
                portfolio_history (List): История изменений портфеля
                final_portfolio_value (float): Конечная стоимость портфеля
                total_trades (int): Общее количество сделок
                symbol (str): Тестируемый символ
                initial_capital (float): Начальный капитал
                backtest_period (Dict): Информация о периоде тестирования

        Исключения:
            ValueError: Если указана неизвестная стратегия или неверные параметры
            Exception: При ошибках загрузки данных или выполнения бэктеста

        Пример:
            >>> service = TradingService()
            >>> # Запуск бэктеста SMA стратегии для Apple
            >>> service_results = service.run_backtest(
            ...     symbol='AAPL',
            ...     strategy_name='sma_crossover',
            ...     start_date='2023-01-01',
            ...     end_date='2023-12-31',
            ...     initial_capital=10000,
            ...     short_window=20,
            ...     long_window=50,
            ...     commission=0.001,  # 0.1% комиссия
            ...     slippage=0.001     # 0.1% проскальзывание
            ... )
            >>> print(f"Общая доходность: {service_results['metrics']['total_return']:.2%}")
            Общая доходность: 15.23%
        """
        # Получение данных
        data = self.data_provider.get_historical_data(symbol, start_date, end_date, interval)

        # Выбор стратегии
        strategy_map = {
            'sma_crossover': SMACrossoverStrategy,
            'ema_crossover': EMACrossoverStrategy,
            'rsi': RSIStrategy,
            'rsi_with_trend': RSIWithTrendStrategy,
            'macd': MACDStrategy,
            'macd_zero_cross': MACDZeroCrossStrategy,
            'combined_rsi_macd': CombinedRSIMACDStrategy
        }

        strategy_class = strategy_map.get(strategy_name)
        if not strategy_class:
            available_strategies = list(strategy_map.keys())
            raise ValueError(f"Неизвестная стратегия: {strategy_name}. Доступные стратегии: {available_strategies}")

        # Валидация параметров стратегии
        self.validate_strategy_parameters(strategy_name, **strategy_params)

        # Запуск бэктеста
        backtester = Backtester(initial_capital=initial_capital, commission=commission, slippage=slippage)
        results = backtester.run_backtest(data, strategy_class, **strategy_params)

        # Сохраняем ссылку на backtester в результатах для возможности сохранения позже
        results['backtester_instance'] = backtester

        # Добавляем расчет PnL для сделок
        if 'trades' in results:
            results['trades'] = self.calculate_trade_pnl(results['trades'])

        return results

    @staticmethod
    def calculate_trade_pnl(trades):
        """Расчет PnL для каждой сделки"""
        position = {}

        for trade in trades:
            symbol = trade['symbol']
            if symbol not in position:
                position[symbol] = {'quantity': 0, 'avg_price': 0, 'realized_pnl': 0}

            # Расчет стоимости сделки
            trade['value'] = trade['quantity'] * round(trade['price'], 2)

            if trade['action'] == 'BUY':
                # Расчет средней цены покупки
                total_quantity = position[symbol]['quantity'] + trade['quantity']
                total_value = (position[symbol]['quantity'] * position[symbol]['avg_price'] +
                               trade['quantity'] * trade['price'])

                if total_quantity > 0:
                    position[symbol]['avg_price'] = total_value / total_quantity
                position[symbol]['quantity'] = total_quantity
                trade['pnl'] = 0  # PnL при покупке = 0
                trade['cumulative_pnl'] = position[symbol]['realized_pnl']

            elif trade['action'] == 'SELL':
                if position[symbol]['quantity'] > 0:
                    # Расчет PnL
                    pnl = (trade['price'] - position[symbol]['avg_price']) * trade['quantity']
                    trade['pnl'] = pnl

                    # Расчет PnL в процентах
                    cost_basis = position[symbol]['avg_price'] * trade['quantity']
                    trade['pnl_percent'] = (pnl / cost_basis * 100) if cost_basis > 0 else 0

                    position[symbol]['realized_pnl'] += pnl
                    trade['cumulative_pnl'] = position[symbol]['realized_pnl']

                    # Уменьшаем позицию
                    position[symbol]['quantity'] -= trade['quantity']
                    if position[symbol]['quantity'] == 0:
                        position[symbol]['avg_price'] = 0
                else:
                    trade['pnl'] = 0
                    trade['cumulative_pnl'] = position[symbol]['realized_pnl']

        return trades

    @staticmethod
    def get_available_strategies() -> dict:
        """
        Возвращает полный список доступных торговых стратегий с описанием и параметрами.

        Возвращает:
            dict: Словарь где ключи - названия стратегий, значения - словари с описанием:
                - description (str): Описание стратегии и принципа работы
                - parameters (dict): Параметры стратегии с типами и значениями по умолчанию

        Пример:
            >>> service = TradingService()
            >>> strategies = service.get_available_strategies()
            >>> for name, info in strategies.items():
            ...     print(f"{name}: {info['description']}")
            ...     for param, details in info['parameters'].items():
            ...         print(f"  {param}: {details['description']} (по умолчанию: {details['default']})")
        """
        return {
            'sma_crossover': {
                'description': 'Стратегия пересечения простых скользящих средних (SMA)',
                'parameters': {
                    'short_window': {'type': int, 'default': 20, 'description': 'Период короткой SMA'},
                    'long_window': {'type': int, 'default': 50, 'description': 'Период длинной SMA'}
                }
            },
            'ema_crossover': {
                'description': 'Стратегия пересечения экспоненциальных скользящих средних (EMA)',
                'parameters': {
                    'short_window': {'type': int, 'default': 12, 'description': 'Период короткой EMA'},
                    'long_window': {'type': int, 'default': 26, 'description': 'Период длинной EMA'}
                }
            },
            'rsi': {
                'description': 'Классическая RSI стратегия на основе зон перекупленности/перепроданности',
                'parameters': {
                    'rsi_window': {'type': int, 'default': 14, 'description': 'Период расчета RSI'},
                    'overbought': {'type': int, 'default': 70, 'description': 'Уровень перекупленности'},
                    'oversold': {'type': int, 'default': 30, 'description': 'Уровень перепроданности'}
                }
            },
            'rsi_with_trend': {
                'description': 'RSI стратегия с учетом направления движения индикатора',
                'parameters': {
                    'rsi_window': {'type': int, 'default': 14, 'description': 'Период расчета RSI'},
                    'overbought': {'type': int, 'default': 70, 'description': 'Уровень перекупленности'},
                    'oversold': {'type': int, 'default': 30, 'description': 'Уровень перепроданности'}
                }
            },
            'macd': {
                'description': 'Классическая MACD стратегия на основе пересечения линий',
                'parameters': {
                    'fast_window': {'type': int, 'default': 12, 'description': 'Период быстрой EMA'},
                    'slow_window': {'type': int, 'default': 26, 'description': 'Период медленной EMA'},
                    'signal_window': {'type': int, 'default': 9, 'description': 'Период сигнальной EMA'}
                }
            },
            'macd_zero_cross': {
                'description': 'MACD стратегия с пересечением нулевой линии',
                'parameters': {
                    'fast_window': {'type': int, 'default': 12, 'description': 'Период быстрой EMA'},
                    'slow_window': {'type': int, 'default': 26, 'description': 'Период медленной EMA'},
                    'signal_window': {'type': int, 'default': 9, 'description': 'Период сигнальной EMA'}
                }
            },
            'combined_rsi_macd': {
                'description': 'Комбинированная стратегия RSI + MACD для фильтрации сигналов',
                'parameters': {
                    'rsi_window': {'type': int, 'default': 14, 'description': 'Период RSI'},
                    'overbought': {'type': int, 'default': 70, 'description': 'Уровень перекупленности'},
                    'oversold': {'type': int, 'default': 30, 'description': 'Уровень перепроданности'},
                    'macd_fast': {'type': int, 'default': 12, 'description': 'Период быстрой EMA MACD'},
                    'macd_slow': {'type': int, 'default': 26, 'description': 'Период медленной EMA MACD'},
                    'macd_signal': {'type': int, 'default': 9, 'description': 'Период сигнальной EMA MACD'}
                }
            }
        }

    def get_strategy_parameters(self, strategy_name: str) -> dict:
        """
        Возвращает параметры и их описания для конкретной стратегии.

        Аргументы:
            strategy_name (str): Название стратегии из списка доступных

        Возвращает:
            dict: Словарь с параметрами стратегии где ключи - названия параметров,
                  значения - словари с информацией о параметре (тип, значение по умолчанию, описание)

        Исключения:
            ValueError: Если указана неизвестная стратегия

        Пример:
            >>> service = TradingService()
            >>> params = service.get_strategy_parameters('sma_crossover')
            >>> print("Параметры SMA стратегии:")
            >>> for param, info in params.items():
            ...     print(f"{param}: {info['description']} (тип: {info['type'].__name__})")
        """
        strategies = self.get_available_strategies()
        if strategy_name not in strategies:
            available_strategies = list(strategies.keys())
            raise ValueError(f"Unknown strategy: {strategy_name}. Available strategies: {available_strategies}")

        return strategies[strategy_name]['parameters']

    def validate_strategy_parameters(self, strategy_name: str, **params) -> bool:
        """
        Проверяет корректность параметров для указанной стратегии.

        Аргументы:
            strategy_name (str): Название стратегии для валидации
            **params: Параметры для проверки

        Возвращает:
            bool: True если все параметры корректны

        Исключения:
            ValueError: Если обнаружены неверные параметры или их значения

        Пример:
            >>> service = TradingService()
            >>> # Корректные параметры
            >>> service.validate_strategy_parameters('sma_crossover', short_window=20, long_window=50)
            True
            >>> # Некорректные параметры (отрицательное значение)
            >>> service.validate_strategy_parameters('sma_crossover', short_window=-10)
            ValueError: Parameter short_window must be positive
        """
        strategy_params = self.get_strategy_parameters(strategy_name)

        for param_name, param_info in strategy_params.items():
            if param_name in params:
                # Проверка типа параметра
                if not isinstance(params[param_name], param_info['type']):
                    raise ValueError(f"Parameter {param_name} must be {param_info['type'].__name__}")

                # Дополнительные проверки для числовых параметров
                if param_info['type'] in [int, float]:
                    if params[param_name] <= 0:
                        raise ValueError(f"Parameter {param_name} must be positive")

        return True