# Algorithmic-Trading-Bot
Торговый бот на Python для тестирования торговых стратегии на исторических данных

## 📁 Структура проекта
    algorithmic_trading_engine/
    │
    ├── config/                   # Конфигурация приложения
    │   ├── __init__.py
    │   ├── settings.py           # Конфигурация
    │   ├── urls.py               # Главные маршруты
    │   ├── asgi.py               # ASGI конфигурация
    │   └── wsgi.py               # WSGI конфигурация
    │
    ├── data/                     # Менеджеры данных
    │   ├── __init__.py
    │   ├── cache.py              # Кэширование данных
    │   ├── data_provider.py      # Абстракция для работы с разными API
    │   └── providers/            # Конкретные реализации провайдеров
    │       ├── __init__.py
    │       └── yahoo_finance.py
    │
    ├── core/                     # Ядро системы - БЭКТЕСТИНГ
    │   ├── __init__.py
    │   ├── logger.py             # Логирование 
    │   ├── backtester.py         # Основной движок бэктестинга
    │   ├── portfolio.py          # Управление портфелем
    │   ├── order_executor.py     # Исполнение ордеров (симуляция)
    │   └── metrics_calculator.py # Расчет метрик (Sharpe, Drawdown etc.)
    │
    ├── indicators/               # ТЕХНИЧЕСКИЕ ИНДИКАТОРЫ
    │   ├── __init__.py
    │   ├── ema.py                # Экспоненциальное скользящее среднее
    │   ├── sma.py                # Cкользяще среднее
    │   ├── rsi.py                # Индекс относительной силы
    │   └── macd.py               # Схождение/расхождение скользящих средних
    │    
    ├── strategies/               # СТРАТЕГИИ (паттерн Strategy)
    │   ├── __init__.py
    │   ├── base_strategy.py      # Абстрактный базовый класс
    │   ├── ma_crossover.py       # Стратегия SMA/EMA
    │   ├── macd_strategy.py      # Стратегия MACD/MACD ZERO
    │   ├── rsi_strategy.py       # Стратегия RSI/RSI TREND
    │   └── rsi_macd_strategy.py  # Стратегия RSI + MACD
    │
    ├── results/                  # ОБРАБОТКА РЕЗУЛЬТАТОВ
    │   ├── __init__.py
    │   ├── visualizer.py         # Генерация графиков
    │   ├── report_generator.py   # Генерация отчетов
    │   └── exporters/            # Экспорт результатов
    │       ├── json_exporter.py
    │       └── csv_exporter.py
    │
    ├── trading/                  # DJANGO APP - WEB ИНТЕРФЕЙС
    │   ├── migrations/
    │   ├── templates/trading/
    │   │   ├── index.html        # Главная страница
    │   │   ├── backtest.html     # Страница бэктестинга
    │   │   ├── results.html      # Результаты
    │   │   └── strategies.html   # Описание стратегий
    │   ├── __init__.py
    │   ├── admin.py              # Админ-панель
    │   ├── apps.py               # Конфигурация приложения
    │   ├── forms.py              # Формы для ввода параметров
    │   ├── models.py             # Модели для сохранения результатов
    │   ├── urls.py               # Маршруты приложения
    │   ├── views.py              # Контроллеры
    │   └── services.py           # Сервисный слой для связи с ядром
    │
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/
    │
    ├── tests/                    # ТЕСТЫ
    │   ├── __init__.py
    │   ├── test_strategies.py
    │   ├── test_backtester.py
    │   └── test_metrics.py
    │
    ├── LICENSE
    ├── manage.py
    ├── README.md
    └── requirements.txt