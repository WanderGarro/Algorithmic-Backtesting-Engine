from django import forms

class BacktestForm(forms.Form):
    """
    Форма для ввода параметров бэктестинга торговых стратегий.
    Содержит общие параметры для всех стратегий и специфические параметры для каждой из поддерживаемых
        торговых стратегий.
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

    symbol = forms.CharField(
        label='Тикер',
        max_length=10,
        initial='AAPL',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Символ акции для тестирования (например: AAPL, TSLA)"
    )

    strategy = forms.ChoiceField(
        label='Стратегия',
        choices=STRATEGY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'strategy-select'}),
        help_text="Выберите торговую стратегию для тестирования"
    )

    start_date = forms.DateField(
        label='Начальная дата',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Дата начала периода тестирования"
    )

    end_date = forms.DateField(
        label='Конечная дата',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Дата окончания периода тестирования"
    )

    initial_capital = forms.DecimalField(
        label='Начальный капитал [$]',
        max_digits=12,
        decimal_places=2,
        initial=10000.00,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Начальная сумма капитала для тестирования"
    )

    commission = forms.DecimalField(
        label='Комиссия [%]',
        max_digits=5,
        decimal_places=3,
        initial=0.001,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0', 'max': '10'}),
        help_text="Размер комиссии в процентах (например, 0.001 = 0.1%)"
    )

    # Параметры для SMA/EMA стратегии
    sma_short_window = forms.IntegerField(
        label='Короткое окно',
        initial=20,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control sma-param ema-param'}),
        help_text="Период короткой скользящей средней"
    )

    sma_long_window = forms.IntegerField(
        label='Длинное окно',
        initial=50,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control sma-param ema-param'}),
        help_text="Период длинной скользящей средней"
    )

    # Параметры для RSI стратегии
    rsi_window = forms.IntegerField(
        label='Период RSI',
        initial=14,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control rsi-param rsi_trend-param combined-param'}),
        help_text="Период расчета индикатора RSI"
    )

    rsi_overbought = forms.IntegerField(
        label='Перекупленность',
        initial=70,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control rsi-param rsi_trend-param combined-param'}),
        help_text="Уровень RSI, считающийся зоной перекупленности"
    )

    rsi_oversold = forms.IntegerField(
        label='Перепроданность',
        initial=30,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control rsi-param rsi_trend-param combined-param'}),
        help_text="Уровень RSI, считающийся зоной перепроданности"
    )

    # Параметры для MACD стратегии
    macd_fast = forms.IntegerField(
        label='Быстрая EMA',
        initial=12,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control macd-param macd_zero-param combined-param'}),
        help_text="Период быстрой EMA для индикатора MACD"
    )

    macd_slow = forms.IntegerField(
        label='Медленная EMA',
        initial=26,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control macd-param macd_zero-param combined-param'}),
        help_text="Период медленной EMA для индикатора MACD"
    )

    macd_signal = forms.IntegerField(
        label='Сигнальная EMA',
        initial=9,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control macd-param macd_zero-param combined-param'}),
        help_text="Период сигнальной линии для индикатора MACD"
    )

    def get_strategy_params(self):
        """
        Извлекает и возвращает параметры стратегии на основе выбранного типа.

        Возвращает:
            dict: Словарь с параметрами для конкретной стратегии. Возвращает только релевантные параметры для
                выбранной стратегии.

        Пример:
            >>> form = BacktestForm({
            ...     'strategy': 'rsi',
            ...     'symbol': 'AAPL',
            ...     'start_date': '2023-01-01',
            ...     'end_date': '2023-12-31',
            ...     'initial_capital': 10000,
            ...     'rsi_window': 14,
            ...     'rsi_overbought': 70,
            ...     'rsi_oversold': 30
            ... })
            >>> if form.is_valid():
            ...     strategy_params = form.get_strategy_params()
            ...     print(strategy_params)
            {'rsi_window': 14, 'overbought': 70, 'oversold': 30}
        """
        strategy = self.cleaned_data['strategy']
        params = {}

        if strategy in ['ema', 'sma']:
            params = {
                'short_window': self.cleaned_data.get('sma_short_window', 20),
                'long_window': self.cleaned_data.get('sma_long_window', 50),
            }
        elif strategy in ['rsi', 'rsi_trend']:
            params = {
                'rsi_window': self.cleaned_data.get('rsi_window', 14),
                'overbought': self.cleaned_data.get('rsi_overbought', 70),
                'oversold': self.cleaned_data.get('rsi_oversold', 30),
            }
        elif strategy in ['macd', 'macd_zero']:
            params = {
                'fast_window': self.cleaned_data.get('macd_fast', 12),
                'slow_window': self.cleaned_data.get('macd_slow', 26),
                'signal_window': self.cleaned_data.get('macd_signal', 9),
            }
        elif strategy == 'combined':
            params = {
                'rsi_window': self.cleaned_data.get('rsi_window', 14),
                'overbought': self.cleaned_data.get('rsi_overbought', 70),
                'oversold': self.cleaned_data.get('rsi_oversold', 30),
                'macd_fast': self.cleaned_data.get('macd_fast', 12),
                'macd_slow': self.cleaned_data.get('macd_slow', 26),
                'macd_signal': self.cleaned_data.get('macd_signal', 9),
            }

        return params