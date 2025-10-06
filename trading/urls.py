from . import views
from django.urls import path

# Конфигурация URL-маршрутов для приложения trading.
# Определяет связь между URL-адресами и представлениями

urlpatterns = [
    # Корневой маршрут приложения.
    # Обрабатывает главную страницу с формой ввода и результатами
    path('', views.index, name='index'),

    path('backtest/', views.backtest_view, name='backtest'),
    path('history/', views.results_history, name='history'),
    path('strategies/', views.strategies_view, name='strategies'),

    path('result/<int:result_id>/', views.result_detail, name='result_detail'),
    path('result/delete/<int:result_id>/', views.delete_result, name='delete_result'),
    path('result/export/<int:result_id>/', views.export_result_to_csv, name='export_result'),
]
