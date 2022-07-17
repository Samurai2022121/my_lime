import logging
from datetime import timedelta
from pathlib import Path

import environ
import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import (
    BreadcrumbHandler,
    EventHandler,
    LoggingIntegration,
)

root = environ.Path(__file__) - 2
env = environ.Env()
env.read_env(root(".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("DJANGO_SECRET_KEY")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

LOGURU_DIAGNOSE = env.bool("LOGURU_DIAGNOSE", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

ENVIRONMENT = env("ENVIRONMENT", default="production")

CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "mptt",
    "drf_yasg",
    "django_filters",
    "rest_framework_simplejwt",
    "django_extensions",
    "haystack",
    "sorl.thumbnail",
    "nested_admin",
    "news",
    "orders",
    "personnel",
    "products",
    "recipes",
    "reviews",
    "internal_api",
    "users",
    "production",
    "discounts",
    "basket",
    "dal",
    "dal_select2",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "lime.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lime.wsgi.application"

DB_NAME = env("DB_NAME")
DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env.int("DB_PORT", default=5432)
DOMAIN = env.int("DOMAIN", default="http://127.0.0.1:8000/")

RF_AUTH_CLASSES = env.list(
    "RF_AUTH_CLASSES",
    default=[
        "users.backends.JWTAuthentication",
    ],
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": RF_AUTH_CLASSES,
    "DEFAULT_PAGINATION_CLASS": "utils.views_utils.DefaultPagination",
    "DATETIME_FORMAT": "%H:%M %d/%m/%Y",
    "DATE_FORMAT": "%d/%m/%Y",
    "TIME_FORMAT": "%H:%M",
}

SWAGGER_SETTINGS = {
    "LOGIN_URL": "admin:login",
    "LOGOUT_URL": "admin:logout",
}

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_BEAT_SCHEDULE = {
    "auto_order": {
        "task": "internal_api.tasks.auto_order",
        "schedule": 60.0,
    },
    "update_search_index": {
        "task": "internal_api.tasks.update_search_index",
        "schedule": 300.0,
    },
}

ACCESS_TOKEN_LIFETIME = timedelta(days=10)
REFRESH_TOKEN_LIFETIME = timedelta(days=11)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Minsk"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/staticfiles/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"
MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = BASE_DIR.parent / "mediafiles"

THUMBNAIL_DEBUG = env.bool("THUMBNAIL_DEBUG", DEBUG)
THUMBNAIL_KVSTORE = "sorl.thumbnail.kvstores.redis_kvstore.KVStore"
THUMBNAIL_BACKEND = "utils.thumbnail.ThumbnailBackend"
THUMBNAIL_PRESERVE_FORMAT = True
THUMBNAIL_REDIS_URL = env("THUMBNAIL_REDIS_URL")

PRODUCT_IMAGE_PRESERVE_ORIGINAL = env.bool("PRODUCT_IMAGE_PRESERVE_ORIGINAL", False)

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "xapian_backend.XapianEngine",
        "HAYSTACK_XAPIAN_LANGUAGE": "ru",
        "PATH": env(
            "xapian_index",
            default=str(BASE_DIR.parent / "xapian_index"),
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SMS_API_KEY = env("SMS_API_KEY", default=None)
SMS_ALPHA_NAME = env("SMS_ALPHA_NAME", default=None)

# Sentry
# https://docs.sentry.io/platforms/python/django/?platform=python

SENTRY_KEY = env("SENTRY_KEY", default=None)
SENTRY_PROJECT = env("SENTRY_PROJECT", default=None)

if SENTRY_KEY and SENTRY_PROJECT:
    sentry_sdk.init(
        dsn="https://{key}@sentry.thefresh.by/{project}".format(
            key=SENTRY_KEY, project=SENTRY_PROJECT
        ),
        integrations=[
            DjangoIntegration(),
            # disable logging integration
            LoggingIntegration(event_level=None, level=None),
        ],
        environment=ENVIRONMENT,
    )
    # add loguru instead of standard logging
    # https://github.com/getsentry/sentry-python/issues/653#issuecomment-788854865
    logger.add(
        BreadcrumbHandler(level=logging.DEBUG),
        diagnose=LOGURU_DIAGNOSE,
        level=logging.DEBUG,
    )
    logger.add(
        EventHandler(level=logging.ERROR),
        diagnose=LOGURU_DIAGNOSE,
        level=logging.ERROR,
    )
