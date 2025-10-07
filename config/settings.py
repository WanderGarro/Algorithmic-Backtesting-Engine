from pathlib import Path
from decouple import config

# Базовые пути проекта
# BASE_DIR - абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность: использование переменных окружения
SECRET_KEY = config('SECRET_KEY', default='django-insecure-7g9paczi+%hw_!kw_sp%46r#n7h7+c*bff*_r+=v7hprke8oa@')

# Безопасность: debug выключен по умолчанию в production
DEBUG = config('DEBUG', default=False, cast=bool)

# Разрешенные хосты с поддержкой Docker
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Определение установленных приложений
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'trading'
]

# Промежуточное ПО (middleware)
# Обрабатывает запросы и ответы в определенном порядке
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',                    # Безопасность
    'django.contrib.sessions.middleware.SessionMiddleware',             # Сессии
    'django.middleware.common.CommonMiddleware',                        # Общие функции
    'django.middleware.csrf.CsrfViewMiddleware',                        # Защита CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',          # Аутентификация
    'django.contrib.messages.middleware.MessageMiddleware',             # Сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware',           # Защита от clickjacking
]

# Корневая конфигурация URL
ROOT_URLCONF = 'config.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',   # Движок шаблонов
        'DIRS': [BASE_DIR / 'trading' / 'templates'],                 # Дополнительные директории шаблонов
        'APP_DIRS': True,                                               # Искать шаблоны в поддиректориях приложений
        'OPTIONS': {
            'context_processors': [                                     # Контекст-процессоры для шаблонов
                'django.template.context_processors.request',           # Объект request
                'django.contrib.auth.context_processors.auth',          # Данные пользователя
                'django.contrib.messages.context_processors.messages',  # Сообщения
            ],
        },
    },
]

# WSGI приложение для развертывания
WSGI_APPLICATION = 'config.wsgi.application'

# Настройки базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',                         # Движок SQLite
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Проверка паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Интернационализация и локализация
LANGUAGE_CODE = 'en-us'     # Язык по умолчанию
TIME_ZONE = 'UTC'           # Часовой пояс по умолчанию
USE_I18N = True             # Включить интернационализацию
USE_TZ = True               # Использовать часовые пояса


# Настройки статических файлов (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Медиа файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип поля для автоматического создания первичных ключей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
        'level': 'ERROR',
    },
}