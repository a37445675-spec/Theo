"""
Configuration Django — Production.
Hérite de settings.py et surcharge pour un environnement de production sécurisé.

Usage :
    set DJANGO_SETTINGS_MODULE=config.settings_production
    python manage.py runserver  # ou gunicorn
"""
from .settings import *  # noqa
from decouple import Config, RepositoryEnv
from pathlib import Path

# === Chargement explicite de .env.production ===
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env.production"

if ENV_FILE.exists():
    config = Config(RepositoryEnv(str(ENV_FILE)))
else:
    from decouple import config


# ============================================================
#  SÉCURITÉ DE BASE
# ============================================================

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# Secret key obligatoire en production
SECRET_KEY = config("SECRET_KEY")
if len(SECRET_KEY) < 50:
    raise ValueError("SECRET_KEY doit faire au moins 50 caractères en production.")


# ============================================================
#  HTTPS / SSL
# ============================================================

# Rediriger HTTP → HTTPS
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

# Cookies sécurisés (uniquement via HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS (HTTP Strict Transport Security) — 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Proxy SSL (utile si derrière Nginx/Traefik)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content Security Policy via headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Referrer Policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# ============================================================
#  COOKIES
# ============================================================

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 jours

CSRF_COOKIE_HTTPONLY = False  # Le JS doit pouvoir lire le cookie
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://nawa.com,https://www.nawa.com",
    cast=lambda v: [s.strip() for s in v.split(",")],
)


# ============================================================
#  CORS
# ============================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="https://nawa.com,https://www.nawa.com",
    cast=lambda v: [s.strip() for s in v.split(",")],
)
CORS_ALLOW_CREDENTIALS = True


# ============================================================
#  BASE DE DONNÉES
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 600,  # 10 minutes
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30 secondes
        },
    }
}


# ============================================================
#  CACHE (Redis)
# ============================================================

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
            "IGNORE_EXCEPTIONS": True,  # Ne pas crasher si Redis tombe
        },
        "KEY_PREFIX": "nawa",
        "TIMEOUT": 300,
    }
}

# Session en cache (plus rapide que DB)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# ============================================================
#  FICHIERS STATIQUES & MÉDIAS
# ============================================================

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Durée de cache des fichiers statiques (1 an)
WHITENOISE_MAX_AGE = 31536000


# ============================================================
#  EMAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="NAWA <no-reply@nawa.com>")


# ============================================================
#  LOGGING PRODUCTION
# ============================================================

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "format": '{{"time": "{asctime}", "level": "{levelname}", "logger": "{name}", "message": "{message}"}}',
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "nawa.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "errors.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
            "level": "ERROR",
        },
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "filters": ["require_debug_false"],
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["error_file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["error_file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# ============================================================
#  SENTRY (monitoring d'erreurs)
# ============================================================

SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=config("SENTRY_ENV", default="production"),
    )


# ============================================================
#  ADMIN SÉCURISÉ
# ============================================================

# Renommer l'URL admin (par défaut /admin/)
ADMIN_URL = config("ADMIN_URL", default="nawa-admin-2026/")


# ============================================================
#  RATE LIMITING
# ============================================================

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = "default"


# ============================================================
#  DIVERS
# ============================================================

# Désactiver la Browsable API en production
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
)

# Désactiver Swagger en production (optionnel)
SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = False

# Performance
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
