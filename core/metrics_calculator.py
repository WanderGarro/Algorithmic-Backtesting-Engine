from numpy import sqrt
from pandas import Series

class MetricsCalculator:
    """Класс для расчета основных финансовых метрик на основе кривой капитала и доходностей."""
    @staticmethod
    def calculate_total_return(equity_curve: Series) -> float:
        """Рассчитывает общую доходность за весь период.

        Параметры:
            equity_curve (Series): Временной ряд значений капитала

        Возвращает:
            float: Общая доходность в десятичной форме (например, 0.15 для 15%)

        Пример:
        >>> equity = Series([100, 105, 110, 95, 120])
        >>> total_return = MetricsCalculator.calculate_total_return(equity)
        """
        return (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

    @staticmethod
    def calculate_sharpe_ratio(returns: Series, risk_free_rate: float = 0.0) -> float:
        """Рассчитывает коэффициент Шарпа - меру доходности с поправкой на риск.

        Параметры:
            returns (Series): Временной ряд дневных доходностей
            risk_free_rate (float, optional): Безрисковая ставка (годовая). По умолчанию 0.0

        Возвращает:
            float: Годовой коэффициент Шарпа

        Особенности:
            Возвращает 0.0 если меньше 2 наблюдений или нулевая волатильность
            Автоматически переводит дневные доходности в годовую формулу

        Пример:
        >>> daily_returns = Series([0.01, -0.02, 0.03, 0.015, -0.01])
        >>> sharpe = MetricsCalculator.calculate_sharpe_ratio(daily_returns, 0.05)
        """
        excess_returns = returns - risk_free_rate / 252
        if len(excess_returns) < 2 or excess_returns.std() == 0:
            return 0.0
        return sqrt(252) * excess_returns.mean() / excess_returns.std()

    @staticmethod
    def calculate_max_drawdown(equity_curve: Series) -> float:
        """Рассчитывает максимальную просадку (максимальное падение от пика до минимума).

        Параметры:
            equity_curve (Series): Временной ряд значений капитала

        Возвращает:
            float: Максимальная просадка в десятичной форме (отрицательное значение)

        Пример:
        >>> equity = Series([100, 120, 90, 110, 85])
        >>> max_dd = MetricsCalculator.calculate_max_drawdown(equity)
        """
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        return drawdown.min()

    @staticmethod
    def calculate_win_rate(returns: Series) -> float:
        """Рассчитывает процент прибыльных сделок (Win Rate).

        Параметры:
            returns (Series): Временной ряд доходностей сделок

        Возвращает:
        float: Доля прибыльных сделок в диапазоне [0, 1]

        Пример:
        >>> trades_returns = Series([0.02, -0.01, 0.03, 0.015, -0.005])
        >>> win_rate = MetricsCalculator.calculate_win_rate(trades_returns)
        """
        winning_trades = returns[returns > 0]
        if len(returns) == 0:
            return 0.0
        return len(winning_trades) / len(returns)