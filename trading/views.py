import csv
from datetime import datetime
from .forms import BacktestForm
from .models import BacktestResult
from .services import TradingService
from .serializers import serialize_backtest_results
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

def index(request):
    """Главная страница приложения для торгового анализа и бэктестинга."""
    return render(request, 'trading/index.html')

def backtest_view(request):
    """
    Представление для запуска и отображения результатов бэктестинга торговых стратегий.
    Использует TradingService для единообразного выполнения бэктестов.

    Обрабатывает GET и POST запросы:
        GET: Отображает форму ввода
        POST: Обрабатывает введенный данные

    Аргументы:
        request (HttpRequest): Объект HTTP запроса от Django.

    Возвращает:
        HttpResponse: Ответ с HTML шаблоном формы или результатов.

    Пример маршрута:
        http://127.0.0.1:8000/
    """
    # Инициализируем торговый сервис
    trading_service = TradingService()

    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            try:
                # Преобразуем данные формы в параметры для TradingService
                strategy_params = _map_form_data_to_strategy_params(form.cleaned_data)

                # Запускаем бэктест через TradingService
                results = trading_service.run_backtest(**strategy_params)

                # Сериализуем результаты
                serialized_data = serialize_backtest_results(results)

                # Обновляем метрики с дополнительной статистикой
                results['metrics'] = serialized_data['metrics']

                # Сохраняем результаты в базу данных
                backtest_result = BacktestResult.objects.create(
                    strategy=form.cleaned_data['strategy'],
                    symbol=form.cleaned_data['symbol'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date'],
                    initial_capital=form.cleaned_data['initial_capital'],
                    total_return=results['metrics']['total_return']*100,
                    sharpe_ratio=results['metrics']['sharpe_ratio'],
                    max_drawdown=results['metrics']['max_drawdown'],
                    win_trades=results['metrics']['winning_trades'],
                    los_trades=results['metrics']['losing_trades'],
                    avg_win=results['metrics']['avg_win'],
                    avg_loss=results['metrics']['avg_loss'],
                    win_rate=results['metrics']['win_rate']*100,
                    strategy_params=form.get_strategy_params(),
                    equity_curve_data=serialized_data['equity_curves_data'],
                    trades_data=serialized_data['trades_data'],
                    final_portfolio_value=results['final_portfolio_value'],
                    total_trades=results['total_trades']
                )

                context = {'form': form, 'result_id': backtest_result.id, 'results': backtest_result}
                
                return render(request, 'trading/results.html', context=context)

            except Exception as e:
                error_message = f'Ошибка при выполнении бэктеста: {str(e)}'
                form.add_error(None, error_message)
                print(f"Backtest error: {e}")
    else:
        # GET запрос - инициализируем форму с разумными датами по умолчанию
        default_start = datetime(2020, 1, 1).date()
        default_end = datetime(2025, 8, 31).date()

        form = BacktestForm(initial={'start_date': default_start, 'end_date': default_end, 'initial_capital': 10000.0})

    return render(request, 'trading/backtest.html', {'form': form})

def _map_form_data_to_strategy_params(form_data):
    """
    Преобразует данные из Django формы в параметры для TradingService.

    Аргументы:
        form_data (dict): Данные из валидированной формы

    Возвращает:
        dict: Параметры в формате, ожидаемом TradingService.run_backtest()
    """
    # Маппинг названий стратегий из формы в имена, используемые в TradingService
    strategy_name_mapping = {
        'sma': 'sma_crossover',
        'ema': 'ema_crossover',
        'rsi': 'rsi',
        'rsi_trend': 'rsi_with_trend',
        'macd': 'macd',
        'macd_zero': 'macd_zero_cross',
        'combined': 'combined_rsi_macd'
    }

    strategy_name = form_data['strategy']
    mapped_strategy_name = strategy_name_mapping.get(strategy_name, strategy_name)

    return {
        'symbol': form_data['symbol'],
        'strategy_name': mapped_strategy_name,
        'start_date': form_data['start_date'].strftime('%Y-%m-%d'),
        'end_date': form_data['end_date'].strftime('%Y-%m-%d'),
        'initial_capital': float(form_data['initial_capital']),
        'interval': '1d',
        'commission': 0.001,
        'slippage': 0.001,
        **form_data.get('strategy_params', {})
    }

def run_backtest(form_data):
    """
    Устаревшая функция. Используйте TradingService напрямую.

    Аргументы:
        form_data (dict): Данные для бэктеста

    Возвращает:
        dict: Результаты бэктеста

    Примечание:
        Эта функция сохраняется для обратной совместимости.
        Рекомендуется использовать TradingService напрямую.
    """
    trading_service = TradingService()
    strategy_params = _map_form_data_to_strategy_params(form_data)
    return trading_service.run_backtest(**strategy_params)

def results_history(request):
    """Отображает историю всех выполненных бэктестов."""
    results = BacktestResult.objects.all().order_by('-created_at')
    return render(request, 'trading/history.html', {'results': results})

def result_detail(request, result_id):
    """Детальное представление конкретного результата бэктеста."""
    backtest_result = get_object_or_404(BacktestResult, id=result_id)
    return render(request, 'trading/result_detail.html', {'result': backtest_result})

def validate_strategy_parameters(request):
    """
    API endpoint для валидации параметров стратегии.

    Аргументы:
        request (HttpRequest): Должен содержать JSON с strategy_name и parameters

    Возвращает:
        JsonResponse: Результат валидации
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)

            trading_service = TradingService()
            is_valid = trading_service.validate_strategy_parameters(data['strategy_name'], **data['parameters'])
            return JsonResponse({'valid': is_valid})

        except Exception as e:
            return JsonResponse({'valid': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def delete_result(request, result_id):
    """Удаление результата бэктеста из базы данных."""
    if request.method == 'POST':
        result = get_object_or_404(BacktestResult, id=result_id)
        result.delete()
        return redirect('history')

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def export_result_to_csv(request, result_id):
    """Экспорт результата бэктеста в CSV файл."""
    backtest_result = get_object_or_404(BacktestResult, id=result_id)

    # Создаем HTTP response с заголовком CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="backtest_result_{result_id}_{backtest_result.symbol}.csv"'

    # Создаем CSV writer с правильной кодировкой
    response.write(u'\ufeff'.encode('utf8'))  # BOM для Excel
    writer = csv.writer(response, delimiter=';')

    # Записываем основные метрики
    writer.writerow(['Метрика', 'Значение'])
    writer.writerow(['Стратегия', backtest_result.strategy])
    writer.writerow(['Тикер', backtest_result.symbol])
    writer.writerow(['Начальная дата', backtest_result.start_date])
    writer.writerow(['Конечная дата', backtest_result.end_date])
    writer.writerow(['Начальный капитал', f"${backtest_result.initial_capital:,.2f}"])
    writer.writerow(['Финальная стоимость портфеля', f"${backtest_result.final_portfolio_value:,.2f}"])
    writer.writerow(['Общая доходность', f"{backtest_result.total_return:.2f}%"])
    writer.writerow(['Коэффициент Шарпа', f"{backtest_result.sharpe_ratio:.2f}"])
    writer.writerow(['Максимальная просадка', f"{backtest_result.max_drawdown:.2f}%"])
    writer.writerow(['Win Rate', f"{backtest_result.win_rate:.1f}%"])
    writer.writerow(['Всего сделок', backtest_result.total_trades])
    writer.writerow(['Прибыльные сделки', backtest_result.win_trades])
    writer.writerow(['Убыточные сделки', backtest_result.los_trades])
    writer.writerow(['Средняя прибыль', f"{backtest_result.avg_win:.2f}%"])
    writer.writerow(['Средний убыток', f"{backtest_result.avg_loss:.2f}%"])
    writer.writerow(['Дата создания', backtest_result.created_at.strftime('%Y-%m-%d %H:%M')])

    # Пустая строка для разделения
    writer.writerow([])

    # Записываем историю сделок
    writer.writerow(['История сделок'])
    writer.writerow(['Дата', 'Действие', 'Цена', 'Количество', 'Стоимость', 'PnL %'])

    try:
        trades_data = backtest_result.trades_data if backtest_result.trades_data else []
        for trade in trades_data:
            writer.writerow([
                trade.get('timestamp', ''),
                trade.get('action', ''),
                f"${trade.get('price', 0):.2f}" if trade.get('price') else '',
                trade.get('quantity', ''),
                f"${trade.get('value', 0):.2f}" if trade.get('value') else '',
                f"{trade.get('pnl_percent', 0):.2f}%" if trade.get('pnl_percent') is not None else ''
            ])
    except Exception as e:
        writer.writerow(['Ошибка при экспорте сделок:', str(e)])

    # Пустая строка для разделения
    writer.writerow([])

    # Записываем данные кривой капитала (первые 10 точек для примера)
    writer.writerow(['Кривая капитала (первые 10 точек)'])
    writer.writerow(['Дата', 'Общая стоимость', 'Денежные средства', 'Стоимость акций'])

    try:
        equity_data = backtest_result.equity_curve_data if backtest_result.equity_curve_data else {}
        dates = list(equity_data.get('total', {}).keys())[:10]  # Берем первые 10 дат

        for date in dates:
            writer.writerow([
                date,
                f"${equity_data.get('total', {}).get(date, 0):.2f}",
                f"${equity_data.get('cash', {}).get(date, 0):.2f}",
                f"${equity_data.get('stocks', {}).get(date, 0):.2f}"
            ])
    except Exception as e:
        writer.writerow(['Ошибка при экспорте кривой капитала:', str(e)])

    return response