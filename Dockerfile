FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создание пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Создание необходимых директорий
RUN mkdir -p static media logs results && \
    chown -R appuser:appuser /app

# Копирование проекта
COPY --chown=appuser:appuser . .

# Переключение на пользователя appuser
USER appuser

# Установка переменной окружения для кэша yfinance
ENV XDG_CACHE_HOME=/tmp/cache
RUN mkdir -p /tmp/cache

# Порт для приложения
EXPOSE 8000

# Команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]