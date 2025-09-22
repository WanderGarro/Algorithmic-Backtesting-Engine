from . import views
from django.urls import path


urlpatterns = [
    path('', views.index, name='index'),
    path('backtest/', views.backtest_view, name='backtest'),
    path('history/', views.results_history, name='history'),
]
