from numpy import cov, sqrt, var
from typing import Dict, List
from pandas import Series, concat

class MetricsCalculator:
    """
    Калькулятор метрик производительности трейдинга.

    Класс предоставляет статические методы для расчета основных финансовых метрик
    на основе кривой капитала и данных о сделках.

    Методы класса позволяют оценивать:
        Общую и годовую доходность
        Рисковые показатели (волатильность, просадки)
        Коэффициенты эффективности (Шарпа, Кальмара)
        Статистику сделок (процент прибыльных, profit factor)
        Бета и альфа относительно бенчмарка
    """

    @staticmethod
    def calculate_total_return(equity_curve: Series) -> float:
        """
        Расчет общей доходности за весь период.

        Аргументы:
            equity_curve (Series): Временной ряд значений капитала (кривая капитала)

        Возвращает:
            float: Общая доходность в десятичной форме (например, 0.15 для 15%)
        """
        if len(equity_curve) < 2:
            return 0.0
        return (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

    @staticmethod
    def calculate_annualized_return(equity_curve: Series, periods_per_year: int = 252) -> float:
        """
        Расчет годовой доходности.

        Аргументы:
        equity_curve (Series): Временной ряд значений капитала
        periods_per_year (int, default=252): Количество торговых периодов в году (по умолчанию 252 дня)

        Возвращает:
            float: Годовая доходность в десятичной форме
        """
        if len(equity_curve) < 2:
            return 0.0

        total_return = MetricsCalculator.calculate_total_return(equity_curve)
        total_periods = len(equity_curve) - 1

        if total_periods <= 0:
            return 0.0

        annualized_return = (1 + total_return) ** (periods_per_year / total_periods) - 1
        return annualized_return

    @staticmethod
    def calculate_volatility(returns: Series, annualize: bool = True) -> float:
        """
        Расчет волатильности (стандартное отклонение доходностей).

        Аргументы:
            returns (Series): Временной ряд доходностей
            annualize (bool, default=True): Флаг годового пересчета волатильности

        Возвращает:
            float: Волатильность в десятичной форме
        """
        if len(returns) < 2:
            return 0.0

        volatility = returns.std()

        if annualize:
            volatility *= sqrt(252)  # Годовая волатильность

        return volatility

    @staticmethod
    def calculate_sharpe_ratio(returns: Series, risk_free_rate: float = 0.0, annualize: bool = True) -> float:
        """
        Расчет коэффициента Шарпа.
        Коэффициент Шарпа показывает отношение избыточной доходности к волатильности.

        Аргументы:
            returns (Series): Временной ряд доходностей
            risk_free_rate (float, default=0.0): Безрисковая ставка в годовом выражении
            annualize (bool, default=True): Флаг годового пересчета коэффициента

        Возвращает:
            float: Коэффициент Шарпа
        """
        if len(returns) < 2 or returns.std() == 0:
            return 0.0

        daily_risk_free = risk_free_rate / 252
        excess_returns = returns - daily_risk_free

        if annualize:
            sharpe = sqrt(252) * excess_returns.mean() / excess_returns.std()
        else:
            sharpe = excess_returns.mean() / excess_returns.std()

        return sharpe

    @staticmethod
    def calculate_max_drawdown(equity_curve: Series) -> float:
        """
        Расчет максимальной просадки.
        Максимальная просадка - это наибольшее падение капитала от пика до минимума.

        Аргументы:
            equity_curve (Series): Временной ряд значений капитала

        Возвращает:
            float: Максимальная просадка в десятичной форме (отрицательное значение)
        """
        if len(equity_curve) == 0:
            return 0.0

        initial_value = equity_curve.iloc[0]
        current_value = equity_curve.iloc[-1]

        # 1. Просадка от начального капитала
        drawdown_from_initial_abs = current_value - initial_value
        drawdown_from_initial_pct = (current_value - initial_value) / initial_value * 100

        # 2. Максимальная просадка от пика (стандартный финансовый показатель)
        peak = equity_curve.expanding().max() # Рассчитываем кумулятивные максимумы
        drawdown_from_peak_abs = equity_curve - peak # Просадка в абсолютных значениях
        drawdown_from_peak_pct = (equity_curve - peak) / peak * 100 # Просадка в процентах

        return abs(drawdown_from_peak_pct.min())

    @staticmethod
    def calculate_calmar_ratio(equity_curve: Series, periods_per_year: int = 252) -> float:
        """
        Расчет коэффициента Кальмара.
        Коэффициент Кальмара - отношение годовой доходности к максимальной просадке.

        Аргументы:
            equity_curve (Series): Временной ряд значений капитала
            periods_per_year (int, default=252): Количество торговых периодов в году

        Возвращает:
            float: Коэффициент Кальмара
        """
        drawdown_info = MetricsCalculator.calculate_max_drawdown(equity_curve)
        max_dd_pct = drawdown_info/ 100

        annual_return = MetricsCalculator.calculate_annualized_return(equity_curve, periods_per_year)

        if max_dd_pct == 0:
            return 0.0

        return annual_return / abs(max_dd_pct)

    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> tuple[int, int, float]:
        """
        Расчет процента прибыльных сделок.
        Сделка считается как завершенная пара (BUY + SELL) или (SELL + BUY).

        Аргументы:
            trades (List[Dict]): Список операций с полями 'action', 'symbol', 'quantity', 'price'

        Возвращает:
            tuple: Количество прибыльных сделок, Количество убыточных сделок, доля прибыльных сделок в диапазоне [0, 1]
        """
        if not trades:
            return 0,0,0.0

        # Группируем операции по символам и находим завершенные сделки
        positions = {}
        completed_trades = []

        # Сортируем сделки по времени
        sorted_trades = sorted(trades, key=lambda x: x.get('timestamp', ''))

        for trade in sorted_trades:
            symbol = trade.get('symbol', 'DEFAULT')
            action = trade.get('action')
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)

            if symbol not in positions:
                positions[symbol] = []

            if action == 'BUY':
                # Добавляем покупку в позицию
                positions[symbol].append({'action': 'BUY', 'quantity': quantity, 'price': price,
                                          'timestamp': trade.get('timestamp'), 'trade_obj': trade})
            elif action == 'SELL':
                # Обрабатываем продажу против существующих покупок
                remaining_sell_qty = quantity

                while remaining_sell_qty > 0 and positions[symbol]:
                    # Берем первую покупку (FIFO)
                    buy_trade = positions[symbol][0]
                    buy_qty = buy_trade['quantity']
                    buy_price = buy_trade['price']

                    # Определяем сколько продаем из этой покупки
                    trade_qty = min(remaining_sell_qty, buy_qty)

                    # Рассчитываем PnL для этой части сделки
                    pnl = (price - buy_price) * trade_qty
                    pnl_percent = (price - buy_price) / buy_price * 100 if buy_price > 0 else 0

                    # Записываем завершенную сделку
                    completed_trades.append({'symbol': symbol, 'buy_price': buy_price, 'sell_price': price,
                                             'quantity': trade_qty, 'pnl': pnl, 'pnl_percent': pnl_percent,
                                             'buy_timestamp': buy_trade['timestamp'],
                                             'sell_timestamp': trade.get('timestamp'), 'is_profitable': pnl > 0})

                    # Обновляем оставшиеся количества
                    remaining_sell_qty -= trade_qty
                    buy_trade['quantity'] -= trade_qty

                    # Если покупка полностью закрыта, удаляем ее
                    if buy_trade['quantity'] == 0:
                        positions[symbol].pop(0)

                # Если осталась непокрытая продажа, считаем как отдельную сделку (шорт)
                if remaining_sell_qty > 0:
                    positions[symbol].append({'action': 'SELL', 'quantity': remaining_sell_qty, 'price': price,
                                              'timestamp': trade.get('timestamp'),'trade_obj': trade})

        # Теперь считаем Win Rate по завершенным сделкам
        if not completed_trades:
            return 0,0,0.0

        profitable_trades = sum(1 for trade in completed_trades if trade['is_profitable'])
        total_completed_trades = len(completed_trades)

        win_rate = profitable_trades / total_completed_trades

        return profitable_trades, total_completed_trades - profitable_trades, win_rate

    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """
        Расчет Profit Factor (отношение суммы прибылей к сумме убытков).

        Аргументы:
            trades (List[Dict]): Список сделок с полями 'action' и 'total'

        Возвращает:
            float: Profit Factor (inf если нет убытков, но есть прибыль)
        """
        gross_loss = 0
        gross_profit = 0

        for trade in trades:
            # Используем PnL если доступен
            if 'pnl' in trade:
                pnl = trade['pnl']
                if pnl > 0:
                    gross_profit += pnl
                else:
                    gross_loss += abs(pnl)
            # Иначе используем старую логику
            elif trade['action'] == 'SELL':
                gross_profit += trade.get('total', 0)
            elif trade['action'] == 'BUY':
                gross_loss += trade.get('total', 0)

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    @staticmethod
    def calculate_beta_alpha(portfolio_returns: Series, benchmark_returns: Series) -> Dict[str, float]:
        """
        Расчет бета и альфа относительно бенчмарка.
        Beta - мера систематического риска.
        Alpha - избыточная доходность относительно ожидаемой по бета.

        Аргументы:
            portfolio_returns (Series): Доходности портфеля
            benchmark_returns (Series): Доходности бенчмарка

        Возвращает:
            Dict[str, float]: Словарь с ключами 'beta' и 'alpha'
        """
        if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
            return {'beta': 0.0, 'alpha': 0.0}

        # Убедимся, что индексы совпадают
        aligned_returns = concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        port_ret = aligned_returns.iloc[:, 0]
        bench_ret = aligned_returns.iloc[:, 1]

        # Расчет бета (ковариация / дисперсия бенчмарка)
        covariance = cov(port_ret, bench_ret)[0, 1]
        benchmark_variance = var(bench_ret)

        beta = covariance / benchmark_variance if benchmark_variance != 0 else 0.0

        # Расчет альфа (средняя доходность портфеля - бета * средняя доходность бенчмарка)
        alpha = port_ret.mean() - beta * bench_ret.mean()

        return {'beta': beta, 'alpha': alpha}

    @staticmethod
    def calculate_all_metrics(equity_curve: Series, trades: List[Dict],risk_free_rate: float =0.0) -> Dict[str, float]:
        """
        Расчет всех основных метрик производительности.

        Аргументы:
            equity_curve (Series): Кривая капитала
            trades (List[Dict]): Список сделок
            risk_free_rate (float, default=0.0): Безрисковая ставка

        Возвращает:
            Dict[str, float]:
            Словарь со всеми рассчитанными метриками:
                total_return: Общая доходность
                annualized_return: Годовая доходность
                volatility: Волатильность
                sharpe_ratio: Коэффициент Шарпа
                max_drawdown: Максимальная просадка
                calmar_ratio: Коэффициент Кальмара
                win_rate: Процент прибыльных сделок
                profit_factor: Profit Factor
                total_trades: Общее количество сделок
        """
        if len(equity_curve) < 2:
            return {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'calmar_ratio': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'total_trades': len(trades),
            }

        returns = equity_curve.pct_change().dropna()

        win_trades, los_trades, win_rate = MetricsCalculator.calculate_win_rate(trades)

        metrics = {
            'total_return': MetricsCalculator.calculate_total_return(equity_curve),
            'annualized_return': MetricsCalculator.calculate_annualized_return(equity_curve),
            'volatility': MetricsCalculator.calculate_volatility(returns),
            'sharpe_ratio': MetricsCalculator.calculate_sharpe_ratio(returns, risk_free_rate),
            'max_drawdown': MetricsCalculator.calculate_max_drawdown(equity_curve),
            'calmar_ratio': MetricsCalculator.calculate_calmar_ratio(equity_curve),
            'winning_trades': win_trades,
            'losing_trades': los_trades,
            'win_rate': win_rate,
            'profit_factor': MetricsCalculator.calculate_profit_factor(trades),
            'total_trades': len(trades),
        }

        return metrics