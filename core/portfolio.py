from core import Logger
from datetime import datetime
from pandas import DataFrame, Series
from typing import Dict, List, Union

class Portfolio:
    """
    Класс для управления торговым портфелем и позициями.

    Отвечает за:
        Учет денежных средств и позиций
        Исполнение торговых операций (покупка/продажа)
        Ведение истории сделок и изменений портфеля
        Расчет текущей стоимости портфеля
        Генерацию отчетов о производительности

    Аргументы:
        initial_cash (float): Начальный капитал портфеля
        cash (float): Текущие денежные средства
        positions (Dict[str, int]): Текущие позиции {символ: количество}
        trade_history (List[Dict]): История всех сделок
        portfolio_history (List[Dict]): История изменений портфеля
        logger (Logger): Логгер для записи событий

    Пример:
        >>> portfolio = Portfolio(initial_cash=10000)
        >>> portfolio.buy("AAPL", 10, 150.0, datetime.now(), "Trend following")
        True
        >>> portfolio.get_position("AAPL")
        10
    """

    def __init__(self, initial_cash: float = 10000.0):
        """
        Инициализация портфеля.

        Аргументы:
            initial_cash (float): Начальный капитал. По умолчанию 10000.0
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, int] = {}
        self.trade_history: List[Dict] = []
        self.portfolio_history: List[Dict] = []
        self.logger = Logger(__name__)

        # Начальная запись в историю
        self._record_portfolio_snapshot(datetime.now(), "Начальное состояние портфеля")
        self.logger.info(f"Портфель инициализирован с начальным капиталом ${initial_cash:.2f}")

    def buy(self, symbol: str, quantity: int, price: float,
            timestamp: datetime, reason: str = "") -> bool:
        """
        Покупка указанного количества акций по заданной цене.

        Аргументы:
            symbol (str): Тикер акции (например, "AAPL")
            quantity (int): Количество акций для покупки
            price (float): Цена покупки за акцию
            timestamp (datetime): Время совершения сделки
            reason (str): Причина покупки (опционально)

        Возвращает:
            bool: True если покупка успешна, False если недостаточно средств

        Пример:
            >>> portfolio = Portfolio(initial_cash=10000)
            >>> portfolio.buy("AAPL", 10, 150.0, datetime.now(), "Пробой уровня")
            True
        """
        total_cost = quantity * price

        if total_cost > self.cash:
            self.logger.warning(f"Недостаточно средств для покупки {quantity} акций {symbol}. "
                                f"Требуется: ${total_cost:.2f}, Доступно: ${self.cash:.2f}")
            return False

        # Исполнение покупки
        self.cash -= total_cost
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity

        # Логирование
        trade_record = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'commission': 0,
            'reason': reason
        }
        self.trade_history.append(trade_record)

        self.logger.info(
                    f"Покупка: {quantity} акций {symbol} по ${price:.2f} (Общая сумма: ${total_cost:.2f}) - {reason}")

        # После сделки записываем снимок с текущей ценой
        current_prices = {symbol: price}
        self._record_portfolio_snapshot(timestamp, f"Покупка {quantity} акций {symbol}", current_prices)

        return True

    def sell(self, symbol: str, quantity: int, price: float, timestamp: datetime, reason: str = "") -> bool:
        """
        Продажа указанного количества акций по заданной цене.

        Аргументы:
            symbol (str): Тикер акции (например, "AAPL")
            quantity (int): Количество акций для продажи
            price (float): Цена продажи за акцию
            timestamp (datetime): Время совершения сделки
            reason (str): Причина продажи (опционально)

        Возвращает:
            bool: True если продажа успешна, False если недостаточно акций

        Пример:
            >>> portfolio = Portfolio(initial_cash=10000)
            >>> portfolio.sell("AAPL", 5, 160.0, datetime.now(), "Фиксация прибыли")
            True
        """
        current_position = self.positions.get(symbol, 0)

        if current_position < quantity:
            self.logger.warning(f"Недостаточно акций {symbol} для продажи. "
                                f"Требуется: {quantity}, В наличии: {current_position}")
            return False

        # Исполнение продажи
        total_revenue = quantity * price
        self.cash += total_revenue
        self.positions[symbol] = current_position - quantity

        # Если позиция закрыта, удаляем из словаря
        if self.positions[symbol] == 0:
            del self.positions[symbol]
            self.logger.info(f"Позиция по {symbol} полностью закрыта")

        # Логирование
        trade_record = {
            'timestamp': timestamp,
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'total': total_revenue,
            'commission': 0,
            'reason': reason
        }
        self.trade_history.append(trade_record)

        self.logger.info(f"Продажа: {quantity} акций {symbol} по ${price:.2f} "
                         f"(Общая сумма: ${total_revenue:.2f}) - {reason}")

        # После сделки записываем снимок с текущей ценой
        current_prices = {symbol: price}
        self._record_portfolio_snapshot(timestamp, f"Продажа {quantity} акций {symbol}", current_prices)

        return True

    def get_position(self, symbol: str) -> int:
        """
        Получение текущего количества акций по символу.

        Аргументы:
            symbol (str): Тикер акции

        Возвращает:
            int: Количество акций в портфеле (0 если отсутствуют)

        Пример:
            >>> portfolio = Portfolio(initial_cash=10000)
            >>> portfolio.get_position("AAPL")
            10
        """
        return self.positions.get(symbol, 0)

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Расчет текущей общей стоимости портфеля.

        Аргументы:
            current_prices (Dict[str, float]): Текущие цены {символ: цена}

        Возвращает:
            float: Общая стоимость портфеля (деньги + акции)

        Пример:
            >>> portfolio = Portfolio(initial_cash=10000)
            >>> portfolio.get_portfolio_value({"AAPL": 155.0})
            10100.0
        """
        stocks_value = sum(quantity * current_prices.get(symbol, 0) for symbol, quantity in self.positions.items())
        portfolio_value = self.cash + stocks_value

        self.logger.debug(f"Расчет стоимости портфеля: наличные ${self.cash:.2f}, "
                          f"акции ${stocks_value:.2f}, общая стоимость ${portfolio_value:.2f}")
        return portfolio_value

    def update_portfolio_value(self, current_prices: Dict[str, float], timestamp: datetime) -> float:
        """
        Обновление и запись текущей стоимости портфеля в историю.

        Аргументы:
            current_prices (Dict[str, float]): Текущие цены акций
            timestamp (datetime): Время обновления

        Возвращает:
            float: Текущая стоимость портфеля
        """
        portfolio_value = self.get_portfolio_value(current_prices)
        self._record_portfolio_snapshot(timestamp, "Периодическое обновление", current_prices)
        self.logger.info(f"Обновлена стоимость портфеля: ${portfolio_value:.2f}")
        return portfolio_value

    def _record_portfolio_snapshot(self, timestamp: datetime, note: str = "",
                                                                    current_prices: Dict[str, float] = None) -> None:
        """
        Внутренний метод для записи снимка состояния портфеля.

        Аргументы:
            timestamp (datetime): Время снимка
            note (str): Примечание к снимку
            current_prices (Dict[str, float]): Текущие цены акций (опционально)
        """
        # Расчет стоимости акций
        stocks_value = 0.0
        if current_prices:
            # Если есть цены, рассчитываем реальную стоимость
            stocks_value = sum(quantity * current_prices.get(symbol, 0) for symbol, quantity in self.positions.items())
        else:
            stocks_value = 0.0
            self.logger.warning(f"⚠️ Нет цен для расчета стоимости акций в снимке {timestamp}")

        total_value = self.cash + stocks_value

        snapshot = {
            'timestamp': timestamp,
            'cash': self.cash,
            'positions': self.positions.copy(),
            'stocks_value': stocks_value,
            'total_value': total_value,
            'note': note
        }
        self.portfolio_history.append(snapshot)

    def get_equity_curve(self, historical_data: DataFrame) -> Dict[str, Series]:
        """
        Расчет кривых капитала: общая стоимость, денежные средства, стоимость акций.

        Аргументы:
            historical_data (DataFrame): Исторические данные цен

        Возвращает:
            Dict: Словарь с кривыми:
                total (Series): общая стоимость портфеля
                cash (Series): денежные средства
                stocks (Series): стоимость акций
        """
        full_dates = historical_data.index

        # Инициализируем серии
        total_curve = Series(index=full_dates, dtype=float)
        cash_curve = Series(index=full_dates, dtype=float)
        stocks_curve = Series(index=full_dates, dtype=float)

        # Если нет истории, используем начальные значения
        if not self.portfolio_history:
            self.logger.warning("⚠️ История портфеля пуста, используем начальные значения")
            total_curve[:] = self.initial_cash
            cash_curve[:] = self.initial_cash
            stocks_curve[:] = 0
            return {'total': total_curve, 'cash': cash_curve, 'stocks': stocks_curve}

        # Заполняем кривые из истории портфеля
        for snapshot in self.portfolio_history:
            snapshot_time = snapshot['timestamp']

            if snapshot_time in total_curve.index:
                total_curve[snapshot_time] = snapshot['total_value']
                cash_curve[snapshot_time] = snapshot['cash']

                # Расчет стоимости акций
                stocks_value = snapshot['total_value'] - snapshot['cash']
                stocks_curve[snapshot_time] = stocks_value

        # Forward fill для заполнения пропусков
        total_curve = total_curve.ffill().bfill().fillna(self.initial_cash)
        cash_curve = cash_curve.ffill().bfill().fillna(self.initial_cash)
        stocks_curve = stocks_curve.ffill().bfill().fillna(0)

        self.logger.info(f"📈 Построены кривые капитала: {len(total_curve)} точек")

        return {'total': total_curve, 'cash': cash_curve, 'stocks': stocks_curve}

    def get_trade_history_df(self) -> DataFrame:
        """
        Преобразование истории сделок в DataFrame.

        Возвращает:
            pd.DataFrame: DataFrame с историей всех сделок
        """
        df = DataFrame(self.trade_history)
        self.logger.info(f"Экспортирована история сделок: {len(df)} записей")
        return df

    def get_portfolio_history_df(self) -> DataFrame:
        """
        Преобразование истории портфеля в DataFrame.

        Возвращает:
            pd.DataFrame: DataFrame с историей изменений портфеля
        """
        df = DataFrame(self.portfolio_history)
        self.logger.info(f"Экспортирована история портфеля: {len(df)} записей")
        return df

    def get_performance_summary(self) -> Dict[str, Union[float, int]]:
        """
        Генерация сводки по производительности портфеля.

        Возвращает:
            Dict: Словарь с метриками производительности

        Пример:
            >>> portfolio = Portfolio(initial_cash=10000)
            >>> portfolio_summary = portfolio.get_performance_summary()
            >>> print(portfolio_summary['win_rate'])
            0.65
        """
        total_trades = len(self.trade_history)
        winning_trades = len([t for t in self.trade_history if t['action'] == 'Продажа'])

        summary = {
            'initial_cash': self.initial_cash,
            'current_cash': self.cash,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'open_positions': len(self.positions),
            'portfolio_value': self.cash + sum(self.positions.values())  # Примерная стоимость
        }

        # Логируем сводку
        self.logger.info(
            f"Сводка производительности: "
            f"Сделки: {total_trades}, "
            f"Успешные: {winning_trades}, "
            f"Процент успеха: {summary['win_rate']:.1%}, "
            f"Открытые позиции: {len(self.positions)}"
        )

        return summary

    def __str__(self) -> str:
        """Строковое представление портфеля."""
        return (f"Портфель(средства=${self.cash:.2f}, "
                f"позиции={len(self.positions)}, "
                f"сделки={len(self.trade_history)})")

    def __repr__(self) -> str:
        """Техническое строковое представление портфеля."""
        return f"Портфель(initial_cash={self.initial_cash})"