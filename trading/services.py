import pandas as pd
from data.data_provider import DataProvider
from core.backtester import Backtester
from strategies import SMACrossoverStrategy, RSIStrategy


class TradingService:
    def __init__(self):
        self.data_provider = DataProvider()

    def run_backtest(self, symbol: str, strategy_name: str,
                     start_date: str, end_date: str,
                     initial_capital: float, **strategy_params):
        # Получение данных
        data = self.data_provider.get_historical_data(
            symbol, start_date, end_date
        )

        # Выбор стратегии
        strategy_map = {
            'sma_crossover': SMACrossoverStrategy,
            'rsi': RSIStrategy,
        }

        strategy_class = strategy_map.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        # Запуск бэктеста
        backtester = Backtester(initial_capital)
        results = backtester.run_backtest(
            data, strategy_class, **strategy_params
        )

        return results
