from django.db import models

class BacktestResult(models.Model):
    """
    Модель для хранения результатов бэктестинга торговых стратегий.
    Содержит основные параметры тестирования, результаты производительности и данные для визуализации
        торговой деятельности.
    """

    STRATEGY_CHOICES = [
        ('ema', 'EMA Crossover'),
        ('sma', 'SMA Crossover'),
        ('rsi', 'RSI Strategy'),
        ('rsi_trend', 'RSI with Trend'),
        ('macd', 'MACD Strategy'),
        ('macd_zero', 'MACD Zero Cross'),
        ('combined', 'Combined RSI/MACD'),
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    strategy = models.CharField(max_length=50, choices=STRATEGY_CHOICES, verbose_name="Стратегия")
    symbol = models.CharField(max_length=10, verbose_name="Тикер")
    start_date = models.DateField(verbose_name="Начальная дата")
    end_date = models.DateField(verbose_name="Конечная дата")
    initial_capital = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Начальный капитал")

    # Результаты
    total_return = models.FloatField(verbose_name="Общая доходность")
    sharpe_ratio = models.FloatField(verbose_name="Коэффициент Шарпа")
    max_drawdown = models.FloatField(verbose_name="Максимальная просадка")
    win_trades = models.PositiveSmallIntegerField(default=0, verbose_name="Количество прибыльных сделок")
    los_trades = models.PositiveSmallIntegerField(default=0, verbose_name="Количество убыточных сделок")
    avg_win = models.FloatField(default=0.0, verbose_name="Средняя прибыль")
    avg_loss = models.FloatField(default=0.0, verbose_name="Средний убыток")
    win_rate = models.FloatField(verbose_name="Процент прибыльных сделок")

    final_portfolio_value = models.FloatField(default=0.0, verbose_name="Конечная стоимость портфеля")
    total_trades = models.IntegerField(default=0, verbose_name="Итог по сделкам")

    # Параметры стратегии
    strategy_params = models.JSONField(default=dict, verbose_name="Параметры стратегии")

    # Данные для графиков
    equity_curve_data = models.JSONField(default=dict, verbose_name="Данные кривой доходности")
    trades_data = models.JSONField(default=dict, verbose_name="Данные сделок")

    class Meta:
        """Мета-класс для дополнительных настроек модели."""
        ordering = ['-created_at']
        verbose_name = "Результат бэктестинга"
        verbose_name_plural = "Результаты бэктестинга"

    def __str__(self):
        """Строковое представление объекта для админки и отладки."""
        return f"{self.strategy} - {self.symbol} - {self.start_date} to {self.end_date}"