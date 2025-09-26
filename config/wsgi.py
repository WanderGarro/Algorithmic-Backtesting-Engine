from os import environ
from django.core.wsgi import get_wsgi_application

# Настройка WSGI (Web Server Gateway Interface) используется для традиционных синхронных серверов типа Gunicorn
environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
