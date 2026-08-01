import os
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', False)

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Библиотеки
    'django_extensions',
    'rest_framework',

    # Приложения
    'web.apps.telegram_users',
    'web.apps.subscriptions',
    'web.apps.payments',
    'web.apps.face_rates',
    'web.apps.consultations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.duckdns.org',
]


ROOT_URLCONF = 'web.core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'web.core.wsgi.application'


POSTGRES_DB = os.getenv('POSTGRES_DB', os.getenv('DB_NAME'))
POSTGRES_USER = os.getenv('POSTGRES_USER', os.getenv('DB_USER'))
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', os.getenv('DB_PASS'))
POSTGRES_HOST = os.getenv('POSTGRES_HOST', os.getenv('DB_HOST', 'localhost'))
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', os.getenv('DB_PORT', 5432)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
REDIS_BROKER_DB = int(os.getenv('REDIS_DB_RATE_LIMIT', 0))
REDIS_RESULT_BACKEND_DB = int(os.getenv('REDIS_DB_RATE_LIMIT', 1))
REDIS_RATE_LIMIT_DB = int(os.getenv('REDIS_DB_RATE_LIMIT', 2))

CELERY_BROKER_URL = f'{REDIS_URL}/{REDIS_BROKER_DB}'
CELERY_RESULT_BACKEND = f'{REDIS_URL}/{REDIS_RESULT_BACKEND_DB}'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': CELERY_BROKER_URL,
        'default_timeout': 60 * 15,
    }
}
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
BOT_LINK = f'https://t.me/{BOT_USERNAME}'
MAX_MESSAGE_PER_SECOND = int(os.getenv('MAX_MESSAGE_PER_SECOND', 1))

TELEGRAM_API_URL = 'https://api.telegram.org'
TELEGRAM_API_TASKS_RATE_LIMIT_KEY = os.getenv(
    'TELEGRAM_API_TASKS_RATE_LIMIT_KEY',
    'telegram_api_tasks_rate_limit'
)
TELEGRAM_API_TASKS_RATE_LIMIT = int(os.getenv('TELEGRAM_API_TASKS_RATE_LIMIT', 15))
TELEGRAM_API_TASKS_RATE_LIMIT_WINDOW = int(os.getenv(
    'TELEGRAM_API_TASKS_RATE_LIMIT_WINDOW', 1
))

PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID')
PRIVATE_CHANNEL_LINK = os.getenv('PRIVATE_CHANNEL_LINK')

DB_BACKUPS_CHAT_ID = os.getenv('DB_BACKUPS_CHAT_ID')

YKASSA_TOKEN = os.getenv('YKASSA_TOKEN')
YKASSA_PAYMENT_EXPIRES_IN_MINUTES = os.getenv('YKASSA_PAYMENT_EXPIRES_IN_MINUTES', 15)

CRYPTO_BOT_API_BASE_URL = os.getenv('CRYPTO_BOT_API_BASE_URL', 'https://pay.crypt.bot/api/')
CRYPTO_BOT_API_TOKEN = os.getenv('CRYPTO_BOT_API_TOKEN')
CRYPTO_BOT_PAYMENT_EXPIRES_IN_MINUTES = os.getenv('YKASSA_PAYMENT_EXPIRES_IN_MINUTES', 60)

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")