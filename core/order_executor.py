from core import Logger
from datetime import datetime

class OrderExecutor:
    """
    Исполнитель ордеров с поддержкой комиссий и проскальзывания.
    Класс отвечает за исполнение торговых операций с учетом реальных условий торговли,
    таких как комиссии биржи и проскальзывание цены при исполнении ордеров.

    Аргументы:
        commission (float): Размер комиссии в процентах (например, 0.001 = 0.1%)
        slippage (float): Размер проскальзывания в процентах (например, 0.001 = 0.1%)
        logger (Logger): Логгер для записи информации о сделках
    """

    def __init__(self, commission: float = 0.001, slippage: float = 0.001):
        """
        Инициализация исполнителя ордеров.

        Аргументы:
            commission (float): Комиссия в процентах (0.1% по умолчанию)
            slippage (float): Проскальзывание в процентах (0.1% по умолчанию)
        """
        self.commission = commission
        self.slippage = slippage
        self.logger = Logger(__name__)

    def calculate_execution_price(self, intended_price: float, action: str) -> float:
        """
        Расчет цены исполнения с учетом проскальзывания.
        Проскальзывание - это разница между ожидаемой ценой и ценой фактического исполнения.
        Для покупки: цена увеличивается (худшая цена для покупателя)
        Для продажи: цена уменьшается (худшая цена для продавца)

        Аргументы:
            intended_price (float): Ожидаемая цена исполнения
            action (str): Тип операции ('BUY' - покупка, 'SELL' - продажа)

        Возвращает:
            float: Цена исполнения с учетом проскальзывания

        Пример:
            >>> executor = OrderExecutor(slippage=0.001)
            >>> executor.calculate_execution_price(100.0, 'BUY')
            ... 100.1 # 100 + 0.1% = 100.1
        """
        slippage_factor = self.slippage * intended_price

        if action == 'BUY':
            execution_price = intended_price + slippage_factor
        elif action == 'SELL':
            execution_price = intended_price - slippage_factor
        else:
            execution_price = intended_price

        return execution_price

    def calculate_commission_cost(self, quantity: int, price: float) -> float:
        """
        Расчет комиссии за сделку.
        Комиссия рассчитывается как процент от общей стоимости сделки.

        Аргументы:
            quantity (int): Количество акций/единиц актива
            price (float): Цена за единицу актива

        Возвращает:
            float: Сумма комиссии в денежном выражении

        Пример:
            >>> executor = OrderExecutor(commission=0.001)
            >>> executor.calculate_commission_cost(10, 100.0)
            ... 1.0  # 10 * 100 * 0.001 = 1.0
        """
        trade_value = quantity * price
        return trade_value * self.commission

    def execute_market_order(self, portfolio, symbol: str, quantity: int, current_price: float, action: str,
                             timestamp: datetime, reason: str = "") -> bool:
        """
        Исполнение рыночного ордера.
        Рыночный ордер исполняется по текущей рыночной цене с учетом проскальзывания и комиссий.

        Аргументы:
            portfolio (Portfolio): Объект портфеля для управления средствами
            symbol (str): Тикер символа (например, 'AAPL')
            quantity (int): Количество акций для покупки/продажи
            current_price (float): Текущая рыночная цена
            action (str): Тип операции ('BUY' или 'SELL')
            timestamp (datetime): Временная метка исполнения ордера
            reason (ыек): Причина исполнения ордера (для логирования)

        Возвращает:
            bool: True если ордер успешно исполнен, False в случае ошибки

        Исключения:
            ValueError: Если указано неверное действие (не 'BUY' или 'SELL')
        """
        # Расчет цены с учетом проскальзывания
        execution_price = self.calculate_execution_price(current_price, action)

        # Расчет комиссии
        commission_cost = self.calculate_commission_cost(quantity, execution_price)

        # Логирование деталей ордера с использованием текущего логгера
        self.logger.info(
            f"Ордер: {action} {quantity} {symbol} - "
            f"Ожидаемая цена: ${current_price:.2f}, "
            f"Цена исполнения: ${execution_price:.2f}, "
            f"Комиссия: ${commission_cost:.2f}"
        )

        # Исполнение через портфель с учетом типа операции
        if action == 'BUY':
            success = portfolio.buy(symbol, quantity, execution_price, timestamp, commission_cost, reason)
            if success:
                self.logger.info(f"Успешная покупка {quantity} {symbol} по цене ${execution_price:.2f}")
            return success

        elif action == 'SELL':
            # Для продажи вычитаем комиссию из выручки
            success = portfolio.sell(symbol, quantity, execution_price, timestamp, commission_cost, reason)
            if success:
                self.logger.info(f"Успешная продажа {quantity} {symbol} по цене ${execution_price:.2f}")
            return success

        else:
            error_msg = f"Неверное действие: {action}. Допустимые значения: 'BUY' или 'SELL'"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def execute_signal(self, portfolio, symbol: str, signal: float, current_price: float, timestamp: datetime,
                       quantity: int = 1, reason: str = "") -> bool:
        """
        Исполнение торгового сигнала.
        Преобразует числовой сигнал в соответствующую торговую операцию.

        Аргументы:
            portfolio (Portfolio): Объект портфеля для управления средствами
            symbol (str): Тикер символа
            signal (float): Торговый сигнал (1 для покупки, -1 для продажи, 0 - бездействие)
            current_price (float): Текущая рыночная цена
            timestamp (datetime): Временная метка исполнения
            quantity (int): Количество акций для торговли (по умолчанию 1)
            reason (str): Причина исполнения сигнала

        Возвращает:
            bool: True если операция исполнена успешно, False если сигнал = 0 или произошла ошибка

        Пример:
            >>> executor = OrderExecutor(commission=0.001)
            >>> executor.execute_signal(portfolio, 'AAPL', 1, 150.0, datetime.now())
            ... # Исполняет ордер на покупку AAPL по цене ~150.0
        """
        if signal > 0:  # Сигнал на покупку
            self.logger.info(f"Получен сигнал на Покупку {symbol}, цена: ${current_price:.2f}")
            return self.execute_market_order(portfolio, symbol, quantity, current_price, 'BUY', timestamp,
                                             f"{reason} - BUY signal")
        elif signal < 0:  # Сигнал на продажу
            self.logger.info(f"Получен сигнал на Продажу {symbol}, цена: ${current_price:.2f}")
            return self.execute_market_order(portfolio, symbol, quantity, current_price, 'SELL', timestamp,
                                             f"{reason} - SELL signal")

        # Сигнал = 0 - бездействие
        self.logger.debug(f"Нулевой сигнал для {symbol} - бездействие")
        return False