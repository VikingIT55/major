import os

from dotenv import load_dotenv
from pathlib import Path
import cloudinary


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    default="django-insecure-vbx=#grju(vl0%2kv)vi16ix4pi-$(q&sffv-egr4y*(fjt@&g",
)
CLOUDINARY_CLOUD_NAME=os.getenv("CLOUDINARY_CLOUD_NAME")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", default="False")

NOVA_POSHTA_API_KEY = os.getenv('NOVA_POSHTA_API_KEY')

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ["karasavaonline.site", "www.karasavaonline.site", "127.0.0.1", "localhost", "*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "users",
    "products",
    "django_filters",
    "cloudinary",
    "cloudinary_storage",
    "delivery",
    "blog",
    "partners",
    "contacts",
    "payments",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "drf_spectacular",
    "drf_spectacular_sidecar",
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
    "django.middleware.locale.LocaleMiddleware",
    "products.middleware.Json404Middleware",
]

ROOT_URLCONF = "config.urls"

CORS_ALLOWED_ORIGINS = [
    "https://karasavaonline.site",
    "https://www.karasavaonline.site",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'uk'
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('en', 'English'),
    ('uk', 'Ukrainian'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale', 
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Support API Documentation",
    "DESCRIPTION": "API Documentation for Support project",
    "VERSION": "v1",
    "SERVE_INCLUDE_SCHEMA": False,
}


SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Basic": {
            "type": "basic",
            "description": "Using Username And Password",
        },
        "Bearer": {
            "type": "apiKey",
            "description": "JSON Web Token Authentication",
            "name": "Authorization",
            "in": "header",
        },
    },
    "DEFAULT_API_URL": "https://karasavaonline.site",
    # can be set as True if needed ability to being authenticated as django user (basic auth)
    "USE_SESSION_AUTH": False,
    # WARNING: This may be a security risk as the credentials are stored unencrypted
    # and can be accessed by all javascript code running on the same domain.
    "PERSIST_AUTH": True,
    "DEFAULT_MODEL_RENDERING": "example",
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
}





cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 60 * 60 * 24,  # 24 hours
    }
}

MONOBANK = {
    "TOKEN": os.getenv("MONOBANK_TOKEN", ""),
    "BASE_URL": os.getenv("MONOBANK_API", "https://api.monobank.ua"),
    "WEBHOOK_PUBLIC_KEY": os.getenv("MONOBANK_WEBHOOK_PUBLIC_KEY", ""),
    "DEFAULT_WEBHOOK_URL": os.getenv("DEFAULT_WEBHOOK_URL", ""),
    "DEFAULT_REDIRECT_URL": os.getenv("DEFAULT_REDIRECT_URL", ""),
    "TIMEOUT": 15,
}


SITE_ID = 2
