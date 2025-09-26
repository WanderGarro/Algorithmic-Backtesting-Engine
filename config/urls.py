from django.contrib import admin
from django.urls import path, include

# Основные URL-маршруты проекта
# Определяет структуру всего веб-приложения

urlpatterns = [
    # Административная панель Django доступна по адресу: http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),

    # Включение URL-маршрутов из приложения trading
    # Все маршруты из trading/urls.py теперь доступны от корня сайта
    path('', include('trading.urls')),
]