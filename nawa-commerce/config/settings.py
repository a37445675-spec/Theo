"""
Configuration Django — NAWA Commerce.

Plateforme e-commerce multi-verticales (cosmétiques, vêtements, chaussures,
électroménager) reposant sur un catalogue à attributs dynamiques, un socle
e-commerce complet, un CMS headless et des briques d'observabilité.

Pour la production :
    DJANGO_SETTINGS_MODULE=config.settings_production
    (voir config/settings_production.py)
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config


# ============================================================
#  CHEMINS DE BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
#  SÉCURITÉ & ENVIRONNEMENT
# ============================================================

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")


# ============================================================
#  APPLICATIONS
# ============================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    # Stockage média
    "cloudinary_storage",
    "cloudinary",
    # REST API
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # UI
    "crispy_forms",
    "crispy_bootstrap5",
    # Async
    "django_celery_beat",
    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

LOCAL_APPS = [
    # Core
    "apps.core",
    "apps.accounts",
    # Catalogue & commerce
    "apps.catalog",
    "apps.cart",
    "apps.checkout",
    "apps.orders",
    "apps.billing",
    "apps.payments",
    "apps.subscriptions",
    "apps.loyalty",
    "apps.promotions",
    "apps.shipping",
    # Contenu & CMS
    "apps.blog",
    "apps.cms",
    "apps.seo",
    "apps.marketing",
    "apps.reporting",
    "apps.observability",
    "apps.integration",
    "apps.platform_settings",
    "apps.pos",
    "apps.b2b",
    "apps.bookings",
    # Modules CMS headless
    "apps.design_system",
    "apps.navigation",
    "apps.translations",
    "apps.feature_flags",
    "apps.announcements",
    "apps.media_library",
    "apps.forms",
    "apps.redirects",
    "apps.third_party_scripts",
    "apps.email_templates",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ============================================================
#  MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.core.middleware.CacheControlMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.observability.middleware.RequestLogMiddleware",
]


# ============================================================
#  URLS & TEMPLATES
# ============================================================

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ============================================================
#  BASE DE DONNÉES
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="nawa_commerce"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="Decembre2"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}


# ============================================================
#  AUTHENTIFICATION
# ============================================================

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# django-allauth
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

SITE_ID = 1

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================================================
#  INTERNATIONALISATION
# ============================================================

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ============================================================
#  FICHIERS STATIQUES & MÉDIAS
# ============================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
#  CLOUDINARY (stockage média en production)
# ============================================================

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

# Si Cloudinary est configuré (clés non vides), l'utiliser comme stockage média par défaut.
# Sinon, les fichiers restent en local (utile pour le développement).
if CLOUDINARY_STORAGE["CLOUD_NAME"] and CLOUDINARY_STORAGE["API_KEY"]:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"


# ============================================================
#  DIVERS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
#  CORS & CSRF
# ============================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://localhost:5173",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000,http://localhost:5173",
    cast=Csv(),
)

# CSRF
CSRF_COOKIE_HTTPONLY = False  # Le JS doit pouvoir lire le cookie
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"


# ============================================================
#  DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.nawa_exception_handler",
}


# ============================================================
#  JWT
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
}


# ============================================================
#  API DOCUMENTATION (drf-spectacular)
# ============================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "NAWA Commerce API",
    "DESCRIPTION": "API REST de la plateforme e-commerce multi-verticales NAWA.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}


# ============================================================
#  UI (crispy forms)
# ============================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ============================================================
#  CELERY (tâches asynchrones)
# ============================================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE


# ============================================================
#  PAIEMENTS
# ============================================================

STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")


# ============================================================
#  EMAILS
# ============================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="NAWA <no-reply@nawa.com>",
)


# ============================================================
#  BUSINESS LOGIC (constantes métier)
# ============================================================

LOYALTY_POINTS_PER_CURRENCY_UNIT = 1
SUBSCRIPTION_DEFAULT_DISCOUNT_PERCENT = 20
FREE_SHIPPING_THRESHOLD = config("FREE_SHIPPING_THRESHOLD", default=49, cast=float)
DEFAULT_CURRENCY = "EUR"