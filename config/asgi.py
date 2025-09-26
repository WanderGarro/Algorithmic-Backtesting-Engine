from os import environ
from django.core.asgi import get_asgi_application

# Настройка ASGI (Asynchronous Server Gateway Interface) используется для асинхронных серверов типа Daphne или Uvicorn
environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
