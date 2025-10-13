import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'proyecto3'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',  #Para CSS/JS
    'app',  #Aplicacion
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'frontend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'app/templates')],
        'APP_DIRS': True,
    },
]

DATABASES = {}

LANGUAGE_CODE = 'es-gt'
TIME_ZONE = 'America/Guatemala'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

#URL del backend Flask
BACKEND_URL = 'http://localhost:5000'