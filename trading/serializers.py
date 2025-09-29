def serialize_backtest_results(results):
    """
    Сериализует результаты бэктеста для отображения в шаблонах и сохранения в БД.

    Аргументы:
        results (dict): Результаты из TradingService.run_backtest()

    Возвращает:
        dict: Сериализованные данные для контекста и сохранения
    """
    # Преобразуем все кривые капитала
    equity_curves_data = {}
    for curve_name, curve_series in results['equity_curves'].items():
        equity_curves_data[curve_name] = {str(timestamp): float(value)  for timestamp, value in curve_series.items()}

    # Сериализуем trades с учетом Timestamp и рассчитываем дополнительные метрики
    trades_data = []

    total_win = 0.0
    total_loss = 0.0
    losing_trades = 0
    winning_trades = 0

    for trade in results['trades']:
        serialized_trade = {}
        for key, value in trade.items():
            if key == 'timestamp' and hasattr(value, 'strftime'):
                # Преобразуем Timestamp в строку без временной зоны
                serialized_trade['date'] = value.strftime('%H:%M:%S %d-%m-%Y ')
            elif key == 'timestamp':
                serialized_trade['date'] = str(value)
            else:
                serialized_trade[key] = value

        # Рассчитываем статистику по сделкам
        if 'pnl_percent' in serialized_trade:
            pnl = serialized_trade['pnl_percent']
            if pnl > 0:
                winning_trades += 1
                total_win += pnl
            elif pnl < 0:
                losing_trades += 1
                total_loss += abs(pnl)

        trades_data.append(serialized_trade)

    # Рассчитываем средние значения
    avg_win = total_win / winning_trades if winning_trades > 0 else 0
    avg_loss = total_loss / losing_trades if losing_trades > 0 else 0

    # Обновляем метрики с дополнительной статистикой
    updated_metrics = results['metrics'].copy()
    updated_metrics.update({
        'avg_win': avg_win,
        'avg_loss': avg_loss,
    })

    return {'equity_curves_data': equity_curves_data, 'trades_data': trades_data, 'metrics': updated_metrics}