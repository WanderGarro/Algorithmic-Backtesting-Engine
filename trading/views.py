from datetime import datetime
from .forms import BacktestForm
from .models import BacktestResult
from django.http import JsonResponse
from core.backtester import Backtester
from django.shortcuts import render, redirect
from strategies import (CombinedRSIMACDStrategy, RSIStrategy, RSIWithTrendStrategy, MACDStrategy, MACDZeroCrossStrategy,
                        EMACrossoverStrategy, SMACrossoverStrategy)


def index(request):
    """Главная страница"""
    return render(request, 'trading/index.html')

def backtest_view(request):
    """Страница бэктестинга"""
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            try:
                # Запускаем бэктест
                results = run_backtest(form.cleaned_data)

                # Сохраняем результаты
                backtest_result = BacktestResult.objects.create(
                    strategy=form.cleaned_data['strategy'],
                    symbol=form.cleaned_data['symbol'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                    initial_capital=form.cleaned_data['initial_capital'],
                    total_return=results['total_return'],
                    sharpe_ratio=results['sharpe_ratio'],
                    max_drawdown=results['max_drawdown'],
                    win_rate=results['win_rate'],
                    strategy_params=form.get_strategy_params(),
                    equity_curve_data=results['equity_curve'].to_dict(),
                    trades_data=results['trades']
                )

                return render(request, 'trading/results.html', {
                    'results': results,
                    'form': form,
                    'result_id': backtest_result.id
                })

            except Exception as e:
                form.add_error(None, f'Ошибка: {str(e)}')
    else:
        # Устанавливаем разумные даты по умолчанию
        default_start = datetime(2020, 1, 1).date()
        default_end = datetime(2025, 8, 31).date()

        form = BacktestForm(initial={'start_date': default_start, 'end_date': default_end})

    return render(request, 'trading/backtest.html', {'form': form})

def run_backtest(form_data):
    """Запуск бэктеста"""
    data_provider = DataProvider()

    # Получаем данные
    data = data_provider.get_historical_data(
        form_data['symbol'],
        form_data['start_date'].strftime('%Y-%m-%d'),
        form_data['end_date'].strftime('%Y-%m-%d')
    )

    # Словарь всех доступных стратегий
    strategy_map = {
        'ema': EMACrossoverStrategy,
        'sma': SMACrossoverStrategy,
        'rsi': RSIStrategy,
        'macd': MACDStrategy,
        'macd_zero': MACDZeroCrossStrategy,
        'rsi_trend': RSIWithTrendStrategy,
        'combined': CombinedRSIMACDStrategy
    }

    strategy_class = strategy_map.get(form_data['strategy'])
    if not strategy_class:
        raise ValueError(f"Unknown strategy: {form_data['strategy']}")

    # Получаем параметры стратегии из формы
    strategy_params = form_data.get('strategy_params', {})

    # Запускаем бэктест
    backtester = Backtester(float(form_data['initial_capital']))
    results = backtester.run_backtest(data, strategy_class, **strategy_params)
    return results

def results_history(request):
    """История результатов"""
    results = BacktestResult.objects.all()
    return render(request, 'trading/history.html', {'results': results})
