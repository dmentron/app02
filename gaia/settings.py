"""
Django settings for gaia project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7$xg&k)2amqg4*mngtkreadlwrgcjw8*_miki7w&&5$3jl0q5b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
PORT_LOCALHOST = ':8082'
NAME_HOST = 'desa'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bases',
    'empresa',
    'seguridad',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gaia.middleware.middleware_menu.menu_middleware_items',
]

ROOT_URLCONF = 'gaia.urls'

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

WSGI_APPLICATION = 'gaia.wsgi.application'

DATABASE_ROUTERS = ['gaia.routers.Cableado']
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gaia',
        'USER': 'osbustaman',
        'PASSWORD': '16090942',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'es'
LOCALE_LANG = 'es_CL.UTF-8'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
SHORT_DATETIME_FORMAT = 'd/m/Y H:M:S.f'
SHORT_DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:M:S.f'
DATE_FORMAT = 'd/m/Y'
DATE_INPUT_FORMATS = ['%d/%m/%Y', '%Y-%m-%d']
DATETIME_INPUT_FORMATS = ['%d/%m/%Y %H:%M:%S.%f', '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']
USE_TZ = True
STATIC_URL = '/static/'
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
IS_WINDOWS = ''

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "templates"),
]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
BASE_COMMAND = IS_WINDOWS + '/home/osvaldo/jab/jab/'
RUTA_PDF = BASE_COMMAND + 'templates/docpdf/'

PYTHON_COMMAND = 'python'  # en el caso de linux es python3

# Tiempo de vida de la sesion en segundos
SESSION_COOKIE_AGE = 10800

# Para que expire la sesion al cerrar el navegador. Por defecto est?? a False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

WKHTMLTOPDF_BIN_PATH = '/usr/local/bin/wkhtmltopdf'

UPLOAD_DIR_FOTO = 'static/'
UPLOAD_DIR = 'static/'
