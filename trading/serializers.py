from datetime import datetime

def serialize_backtest_results(results):
    """
    Сериализует результаты бэктеста для отображения в шаблонах и сохранения в БД.

    Функция преобразует сырые данные бэктеста в структурированный формат, подходящий
    для отображения в шаблонах Django и сохранения в модели БД. Включает:
        Кривые капитала (общая стоимость, денежные средства, стоимость акций)
        Точки сделок (покупки и продажи) для отображения на графике
        Статистику по сделкам и метрики производительности

    Аргументы:
        results (dict): Результаты из TradingService.run_backtest(), содержащий:
            equity_curves (dict): Кривые капитала с временными метками
            trades (list): Список сделок с деталями
            metrics (dict): Рассчитанные метрики производительности

    Возвращает:
        dict: Сериализованные данные в формате:
            {
                'equity_curves_data': {
                    'total': {date_str: value},
                    'cash': {date_str: value},
                    'stocks': {date_str: value},
                    'buy_points': {date_str: value},  # Точки покупок
                    'sell_points': {date_str: value}  # Точки продаж
                },
                'trades_data': [list сериализованных сделок],
                'metrics': dict обновленных метрик
            }
    """
    # Преобразуем все кривые капитала в сериализуемый формат
    equity_curves_data = {}
    for curve_name, curve_series in results['equity_curves'].items():
        equity_curves_data[curve_name] = {str(timestamp): float(value) for timestamp, value in curve_series.items()}

    # Инициализируем словари для точек сделок на графике
    equity_curves_data['buy_points'] = {}
    equity_curves_data['sell_points'] = {}

    trades_data = []
    total_win = 0.0
    total_loss = 0.0
    losing_trades = 0
    winning_trades = 0

    # Создаем mapping оригинальных дат для сопоставления сделок с точками на кривой капитала
    original_dates_mapping = {}
    if 'total' in equity_curves_data:
        for original_date_str in equity_curves_data['total'].keys():
            try:
                # Обрабатываем различные форматы дат (с временной зоной и без)
                date_obj = None
                try:
                    date_obj = datetime.strptime(original_date_str, '%Y-%m-%d %H:%M:%S%z')
                except ValueError:
                    try:
                        date_obj = datetime.strptime(original_date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            date_obj = datetime.strptime(original_date_str, '%Y-%m-%d')
                        except ValueError:
                            continue

                if date_obj:
                    # Создаем нормализованный ключ для поиска по дате (без времени)
                    normalized_key = date_obj.strftime('%Y-%m-%d')
                    original_dates_mapping[normalized_key] = original_date_str
            except Exception:
                continue

    # Обрабатываем сделки для создания точек на графике и статистики
    for trade in results['trades']:
        serialized_trade = {}

        for key, value in trade.items():
            if key == 'timestamp' and hasattr(value, 'strftime'):
                # Нормализуем дату сделки (убираем временную зону если есть)
                trade_date = value.replace(tzinfo=None) if value.tzinfo else value
                serialized_trade['date'] = trade_date.strftime('%H:%M:%S %d-%m-%Y')

                # Создаем ключ для поиска в формате YYYY-MM-DD
                trade_date_key = trade_date.strftime('%Y-%m-%d')

                # Ищем соответствующую дату в оригинальных данных кривой капитала
                matching_original_date = original_dates_mapping.get(trade_date_key)

                if matching_original_date:
                    equity_value = equity_curves_data['total'].get(matching_original_date)
                    if equity_value is not None:
                        # Сохраняем точку сделки используя оригинальный ключ даты
                        if trade['action'] == 'BUY':
                            equity_curves_data['buy_points'][matching_original_date] = equity_value
                        elif trade['action'] == 'SELL':
                            equity_curves_data['sell_points'][matching_original_date] = equity_value

            elif key == 'timestamp':
                serialized_trade['date'] = str(value)
            else:
                serialized_trade[key] = value

        # Собираем статистику по сделкам для расчета метрик
        if 'pnl_percent' in serialized_trade:
            pnl = serialized_trade['pnl_percent']
            if pnl > 0:
                winning_trades += 1
                total_win += pnl
            elif pnl < 0:
                losing_trades += 1
                total_loss += abs(pnl)

        trades_data.append(serialized_trade)

    # Рассчитываем дополнительные метрики на основе статистики сделок
    avg_win = total_win / winning_trades if winning_trades > 0 else 0
    avg_loss = total_loss / losing_trades if losing_trades > 0 else 0

    # Обновляем метрики с рассчитанными значениями
    updated_metrics = results['metrics'].copy()
    updated_metrics.update({'avg_win': avg_win, 'avg_loss': avg_loss,})

    return {'equity_curves_data': equity_curves_data, 'trades_data': trades_data, 'metrics': updated_metrics}