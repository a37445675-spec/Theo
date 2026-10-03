"""
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
    print("\n⚠️  Assurez-vous d'avoir créé un fichier .env.production")
    print("   et d'avoir installé les dépendances : pip install -r requirements.txt")
    sys.exit(1)

from django.conf import settings


# Couleurs
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


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
        print(f"\n  {GREEN}{BOLD}🎉 CONFIGURATION PRODUCTION PRÊTE{RESET}")
    elif passed >= total * 0.9:
        print(f"\n  {YELLOW}{BOLD}⚠️  Configuration quasi-complète{RESET}")
    else:
        print(f"\n  {RED}{BOLD}❌ Configuration incomplète{RESET}")

    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")

    return 0 if passed >= total * 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
