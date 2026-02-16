
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-n2u)cupmij=a#p9yp-km!&*@=io0fnsb@)7qqun^g-x263+&r0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scraper',  # scraper app
    'django_celery_results',
    'django_celery_beat',
    
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


ROOT_URLCONF = 'Amaze.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # template directory
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

WSGI_APPLICATION = 'Amaze.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {'sslmode': 'require'}, # Ensure secure connection
        'CONN_MAX_AGE': 300 
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'scraper/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For production

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL","your_url")
SUPABASE_KEY = os.getenv("SUPABASE_KEY","anon-key")

# Site URL (For Google OAuth redirect)
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")

# 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

AUTH_USER_MODEL = 'scraper.CustomUser'  # Replace `CustomUser` with your actual model name

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Celery Settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")

# Celery Task Settings
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE  = "Asia/Kolkata"

# Celery Beat Scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# SMTP Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER ='sudhanshun10b3720@gmail.com'
EMAIL_HOST_PASSWORD = "eniyaihhuizttotg"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

import logging
logging.basicConfig(level=logging.DEBUG)

ASGI_APPLICATION = "Amaze.asgi.application"

# ScraperAPI Key
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

