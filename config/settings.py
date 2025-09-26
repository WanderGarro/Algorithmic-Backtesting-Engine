from pathlib import Path

# Базовые пути проекта
# BASE_DIR - абсолютный путь к директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# ВАЖНО ДЛЯ БЕЗОПАСНОСТИ: храните секретный ключ в секрете в production!
SECRET_KEY = 'django-insecure-7g9paczi+%hw_!kw_sp%46r#n7h7+c*bff*_r+=v7hprke8oa@'

# ВАЖНО ДЛЯ БЕЗОПАСНОСТИ: не включайте debug в production!
DEBUG = True

# Разрешенные хосты (для production добавьте доменные имена)
ALLOWED_HOSTS = []

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
        'DIRS': [],                                                     # Дополнительные директории шаблонов
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

# Тип поля для автоматического создания первичных ключей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'