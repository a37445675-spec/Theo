"""
Phase 12.1 — Sécurité & Settings Production.
Configure le backend Django pour un déploiement en production sécurisé.

Usage : python setup_production_security.py
"""
import os
import re
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.py")
PROD_SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings_production.py")
ENV_EXAMPLE_PATH = os.path.join(BASE_DIR, ".env.example")
ENV_PROD_PATH = os.path.join(BASE_DIR, ".env.production")
CHECK_SCRIPT_PATH = os.path.join(BASE_DIR, "check_production.py")
LOGS_DIR = os.path.join(BASE_DIR, "logs")


# ============================================================
#              PRODUCTION SETTINGS
# ============================================================

PRODUCTION_SETTINGS = '''"""
Configuration Django — Production.
Hérite de settings.py et surcharge pour un environnement de production sécurisé.

Usage :
    set DJANGO_SETTINGS_MODULE=config.settings_production
    python manage.py runserver  # ou gunicorn
"""
from .settings import *  # noqa
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
    "rest_framework.renderers.JSONRenderer",
)

# Désactiver Swagger en production (optionnel)
SPECTACULAR_SETTINGS["SERVE_INCLUDE_SCHEMA"] = False

# Performance
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
'''


# ============================================================
#              .env.example
# ============================================================

ENV_EXAMPLE = '''# ============================================================
#  NAWA Commerce — Variables d'environnement
#  Copiez ce fichier en .env.production et remplissez les valeurs
# ============================================================

# === Django ===
SECRET_KEY=changez-moi-par-une-cle-secrete-de-50-caracteres-minimum-xxxxx
DEBUG=False
ALLOWED_HOSTS=nawa.com,www.nawa.com,localhost,127.0.0.1

# === Base de données ===
DB_NAME=nawa_commerce
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432

# === Redis ===
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# === Frontend ===
FRONTEND_URL=https://nawa.com
CORS_ALLOWED_ORIGINS=https://nawa.com,https://www.nawa.com
CSRF_TRUSTED_ORIGINS=https://nawa.com,https://www.nawa.com

# === Sécurité HTTPS ===
SECURE_SSL_REDIRECT=True

# === Admin URL (par défaut /admin/) ===
ADMIN_URL=nawa-admin-2026/

# === Email (SMTP) ===
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=contact@nawa.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
DEFAULT_FROM_EMAIL=NAWA <no-reply@nawa.com>

# === Monitoring (optionnel) ===
SENTRY_DSN=
SENTRY_ENV=production

# === Paiement (optionnel) ===
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# === Paiement (PayPal) ===
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
'''


# ============================================================
#              CHECK SCRIPT
# ============================================================

CHECK_SCRIPT = '''"""
Vérification de la configuration production.
Lance ce script avant tout déploiement.

Usage : python check_production.py
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_production")

try:
    import django
    django.setup()
except Exception as e:
    print(f"❌ Erreur d'initialisation Django : {e}")
    print("\\n⚠️  Assurez-vous d'avoir créé un fichier .env.production")
    print("   et d'avoir installé les dépendances : pip install -r requirements.txt")
    sys.exit(1)

from django.conf import settings


# Couleurs
RED = "\\033[91m"
GREEN = "\\033[92m"
YELLOW = "\\033[93m"
CYAN = "\\033[96m"
BOLD = "\\033[1m"
RESET = "\\033[0m"


def check(label, condition, critical=True):
    icon = f"{GREEN}✅{RESET}" if condition else f"{RED}❌{RESET}" if critical else f"{YELLOW}⚠️ {RESET}"
    print(f"  {icon} {label}")
    return condition


def main():
    print()
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  AUDIT DE SÉCURITÉ PRODUCTION{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")
    print()

    checks = []

    # === Paramètres essentiels ===
    print(f"{BOLD}🔒 Paramètres essentiels{RESET}")
    checks.append(check("DEBUG = False", settings.DEBUG is False))
    checks.append(check("SECRET_KEY longue (>= 50)", len(settings.SECRET_KEY) >= 50))
    checks.append(check("ALLOWED_HOSTS configuré", len(settings.ALLOWED_HOSTS) > 0))
    print()

    # === HTTPS ===
    print(f"{BOLD}🔐 HTTPS / SSL{RESET}")
    checks.append(check("SECURE_SSL_REDIRECT", getattr(settings, "SECURE_SSL_REDIRECT", False)))
    checks.append(check("SESSION_COOKIE_SECURE", getattr(settings, "SESSION_COOKIE_SECURE", False)))
    checks.append(check("CSRF_COOKIE_SECURE", getattr(settings, "CSRF_COOKIE_SECURE", False)))
    checks.append(check("HSTS actif (>= 1 an)", getattr(settings, "SECURE_HSTS_SECONDS", 0) >= 31536000))
    checks.append(check("HSTS IncludeSubDomains", getattr(settings, "SECURE_HSTS_INCLUDE_SUBDOMAINS", False)))
    checks.append(check("HSTS Preload", getattr(settings, "SECURE_HSTS_PRELOAD", False), critical=False))
    print()

    # === Headers de sécurité ===
    print(f"{BOLD}🛡️  Headers de sécurité{RESET}")
    checks.append(check("X_FRAME_OPTIONS = DENY", getattr(settings, "X_FRAME_OPTIONS", "") == "DENY"))
    checks.append(check("SECURE_CONTENT_TYPE_NOSNIFF", getattr(settings, "SECURE_CONTENT_TYPE_NOSNIFF", False)))
    checks.append(check("SECURE_BROWSER_XSS_FILTER", getattr(settings, "SECURE_BROWSER_XSS_FILTER", False)))
    checks.append(check("SECURE_REFERRER_POLICY défini", bool(getattr(settings, "SECURE_REFERRER_POLICY", ""))))
    print()

    # === Cookies ===
    print(f"{BOLD}🍪 Cookies{RESET}")
    checks.append(check("SESSION_COOKIE_HTTPONLY", getattr(settings, "SESSION_COOKIE_HTTPONLY", False)))
    checks.append(check("SESSION_COOKIE_SAMESITE", getattr(settings, "SESSION_COOKIE_SAMESITE", "") == "Lax"))
    checks.append(check("CSRF_COOKIE_SAMESITE", getattr(settings, "CSRF_COOKIE_SAMESITE", "") == "Lax"))
    checks.append(check("CSRF_TRUSTED_ORIGINS configuré", len(getattr(settings, "CSRF_TRUSTED_ORIGINS", [])) > 0))
    print()

    # === Base de données ===
    print(f"{BOLD}💾 Base de données{RESET}")
    db = settings.DATABASES.get("default", {})
    checks.append(check("PostgreSQL", db.get("ENGINE", "").endswith("postgresql")))
    checks.append(check("CONN_MAX_AGE >= 60s", db.get("CONN_MAX_AGE", 0) >= 60, critical=False))
    checks.append(check("Statement timeout configuré", "statement_timeout" in str(db.get("OPTIONS", {}))))
    print()

    # === Cache ===
    print(f"{BOLD}⚡ Cache{RESET}")
    cache = settings.CACHES.get("default", {})
    checks.append(check("Cache Redis", "Redis" in cache.get("BACKEND", ""), critical=False))
    checks.append(check("Session en cache", "cache" in settings.SESSION_ENGINE, critical=False))
    print()

    # === Fichiers statiques ===
    print(f"{BOLD}📁 Fichiers statiques{RESET}")
    checks.append(check("STATIC_ROOT défini", bool(settings.STATIC_ROOT)))
    checks.append(check("Whitenoise configuré", "whitenoise" in settings.STATICFILES_STORAGE.lower()))
    checks.append(check("Cache statique (1 an)", getattr(settings, "WHITENOISE_MAX_AGE", 0) >= 31536000, critical=False))
    print()

    # === API ===
    print(f"{BOLD}🌐 API{RESET}")
    renderers = settings.REST_FRAMEWORK.get("DEFAULT_RENDERER_CLASSES", [])
    checks.append(check("Browsable API désactivée", "BrowsableAPIRenderer" not in str(renderers), critical=False))
    print()

    # === Logging ===
    print(f"{BOLD}📝 Logging{RESET}")
    checks.append(check("Logging configuré", hasattr(settings, "LOGGING")))
    checks.append(check("Log file défini", "file" in str(getattr(settings, "LOGGING", {}).get("handlers", {}))))
    print()

    # === Résumé ===
    total = len(checks)
    passed = sum(checks)
    critical_passed = True

    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}  RÉSUMÉ{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"  Tests passés : {GREEN}{passed}{RESET}/{total}")

    if passed == total:
        print(f"\\n  {GREEN}{BOLD}🎉 CONFIGURATION PRODUCTION PRÊTE{RESET}")
    elif passed >= total * 0.9:
        print(f"\\n  {YELLOW}{BOLD}⚠️  Configuration quasi-complète{RESET}")
    else:
        print(f"\\n  {RED}{BOLD}❌ Configuration incomplète{RESET}")

    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\\n")

    return 0 if passed >= total * 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
'''


# ============================================================
#              FONCTIONS
# ============================================================

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, content, backup=True):
    ensure_dir(os.path.dirname(path))
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        if backup:
            shutil.copy2(path, path + ".bak")
            print(f"  [BACKUP] {label}.bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def backup_settings():
    if os.path.exists(SETTINGS_PATH):
        shutil.copy2(SETTINGS_PATH, SETTINGS_PATH + ".before-prod.bak")
        print(f"  [BACKUP] config/settings.py.before-prod.bak")


def update_settings_module():
    """Note dans settings.py que la version prod existe."""
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "settings_production" in content:
        print("  [SKIP] settings.py déjà mis à jour")
        return

    note = '''"""
Configuration Django — NAWA Commerce.

⚠️  Pour la production, utilisez :
    DJANGO_SETTINGS_MODULE=config.settings_production
    (voir config/settings_production.py)
"""
'''
    # Remplacer le docstring existant
    content = re.sub(
        r'^""".*?"""\s*',
        note + "\n",
        content,
        count=1,
        flags=re.DOTALL,
    )

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] config/settings.py annoté")


def update_requirements():
    """Ajoute les dépendances production."""
    req_path = os.path.join(BASE_DIR, "requirements.txt")
    if not os.path.exists(req_path):
        print("  [INFO] requirements.txt introuvable, ignoré")
        return

    with open(req_path, "r", encoding="utf-8") as f:
        content = f.read()

    additions = []
    packages = [
        "django-redis>=5.4.0",
        "django-ratelimit>=4.1.0",
        "sentry-sdk>=2.0.0",
        "gunicorn>=22.0.0",
        "whitenoise>=6.7.0",
        "psycopg2-binary>=2.9.9",
    ]

    for pkg in packages:
        name = pkg.split(">=")[0].split("==")[0]
        if name.lower() not in content.lower():
            additions.append(pkg)

    if additions:
        with open(req_path, "a", encoding="utf-8") as f:
            f.write("\n# === Production (Phase 12.1) ===\n")
            f.write("\n".join(additions) + "\n")
        print(f"  [OK] {len(additions)} package(s) ajouté(s) à requirements.txt")
    else:
        print("  [SKIP] requirements.txt déjà à jour")


def create_logs_dir():
    ensure_dir(LOGS_DIR)
    gitignore = os.path.join(LOGS_DIR, ".gitignore")
    with open(gitignore, "w") as f:
        f.write("*\n!.gitignore\n")
    print("  [OK] logs/ créé avec .gitignore")


def update_gitignore():
    """Ajoute les fichiers sensibles au .gitignore."""
    gi_path = os.path.join(BASE_DIR, ".gitignore")
    entries = [
        ".env",
        ".env.production",
        ".env.local",
        "*.log",
        "logs/",
        "staticfiles/",
        "media/",
        "*.bak",
    ]

    existing = ""
    if os.path.exists(gi_path):
        with open(gi_path, "r", encoding="utf-8") as f:
            existing = f.read()

    missing = [e for e in entries if e not in existing]
    if missing:
        with open(gi_path, "a", encoding="utf-8") as f:
            f.write("\n# === Phase 12.1 — Production ===\n")
            f.write("\n".join(missing) + "\n")
        print(f"  [OK] .gitignore enrichi ({len(missing)} entrées)")
    else:
        print("  [SKIP] .gitignore déjà à jour")


# ============================================================
#              MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 12.1 — SÉCURITÉ & SETTINGS PRODUCTION")
    print("=" * 60)

    if not os.path.exists(SETTINGS_PATH):
        print(f"\n  ❌ settings.py introuvable dans {CONFIG_DIR}")
        print("  → Êtes-vous bien à la racine de nawa-commerce ?")
        sys.exit(1)

    print("\n[1/6] Sauvegarde de settings.py...")
    backup_settings()

    print("\n[2/6] Création de settings_production.py...")
    write_file(PROD_SETTINGS_PATH, PRODUCTION_SETTINGS)

    print("\n[3/6] Annotation de settings.py...")
    update_settings_module()

    print("\n[4/6] Création des templates .env...")
    write_file(ENV_EXAMPLE_PATH, ENV_EXAMPLE, backup=False)
    if not os.path.exists(ENV_PROD_PATH):
        write_file(ENV_PROD_PATH, ENV_EXAMPLE, backup=False)
        print("  [INFO] .env.production créé — REMPLISSEZ les valeurs !")
    else:
        print("  [SKIP] .env.production existe déjà")

    print("\n[5/6] Mise à jour de requirements.txt...")
    update_requirements()

    print("\n[6/6] Fichiers annexes...")
    create_logs_dir()
    update_gitignore()
    write_file(CHECK_SCRIPT_PATH, CHECK_SCRIPT, backup=False)

    print()
    print("=" * 60)
    print("  ✅ PHASE 12.1 TERMINÉE")
    print("=" * 60)
    print("\nFichiers créés :")
    print("  config/settings_production.py    — Settings prod sécurisés")
    print("  .env.example                     — Template variables")
    print("  .env.production                  — À REMPLIR")
    print("  check_production.py              — Audit automatique")
    print("  logs/                            — Répertoire de logs")
    print()
    print("⚠️  PROCHAINES ÉTAPES :")
    print()
    print("  1. Remplir .env.production :")
    print("     notepad .env.production")
    print()
    print("  2. Installer les nouvelles dépendances :")
    print("     pip install -r requirements.txt")
    print()
    print("  3. Tester la config prod :")
    print("     $env:DJANGO_SETTINGS_MODULE = 'config.settings_production'")
    print("     python check_production.py")


if __name__ == "__main__":
    main()