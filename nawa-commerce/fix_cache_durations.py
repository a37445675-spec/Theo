"""
Réduit les durées de cache pour les données modifiables en temps réel.
Permet aux modifications de l'admin d'apparaître en quelques secondes.

Usage : python fix_cache_durations.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MIDDLEWARE_PATH = os.path.join(BASE_DIR, "apps", "core", "middleware.py")


# ============================================================
#  NOUVELLE CONFIG CACHE (durées réduites)
# ============================================================

NEW_CACHE_CONFIG = '''    # Endpoints publics cacheables (regex, durée en secondes)
    # Durées courtes pour permettre des modifications rapides depuis l'admin.
    PUBLIC_CACHE = [
        # Contenu CMS modifiable fréquemment
        (r"^/api/v1/navigation/", 30),           # 30 secondes
        (r"^/api/v1/announcements/", 30),        # 30 secondes
        (r"^/api/v1/feature-flags/", 30),        # 30 secondes
        (r"^/api/v1/design-system/", 30),        # 30 secondes
        (r"^/api/v1/translations/", 60),         # 1 minute
        (r"^/api/v1/media-library/", 300),       # 5 minutes
        (r"^/api/v1/redirects/", 60),            # 1 minute
        (r"^/api/v1/seo/", 300),                 # 5 minutes
        # Catalogue
        (r"^/api/v1/catalog/categories/", 60),   # 1 minute
        (r"^/api/v1/catalog/products/", 30),     # 30 secondes
        # Blog
        (r"^/api/v1/blog/categories/", 60),      # 1 minute
        (r"^/api/v1/blog/tags/", 60),            # 1 minute
        (r"^/api/v1/blog/posts/", 30),           # 30 secondes
    ]'''


# ============================================================
#  SIGNAL DE PURGE DU CACHE (backend)
# ============================================================

CACHE_SIGNALS = '''
# ============================================================
#  PURGE AUTOMATIQUE DU CACHE (backend)
# ============================================================

"""
Signaux Django qui vident le cache quand on modifie
les modèles critiques (menus, annonces, flags, design system).
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


@receiver([post_save, post_delete])
def invalidate_navigation_cache(sender, instance, **kwargs):
    """Purge le cache quand un Menu ou MenuItem change."""
    if sender.__name__ in ("Menu", "MenuItem"):
        _purge_api_cache("navigation")


@receiver([post_save, post_delete])
def invalidate_announcement_cache(sender, instance, **kwargs):
    """Purge le cache quand une Annonce change."""
    if sender.__name__ in ("Announcement",):
        _purge_api_cache("announcements")


@receiver([post_save, post_delete])
def invalidate_design_system_cache(sender, instance, **kwargs):
    """Purge le cache quand le Design System change."""
    if sender.__name__ in ("DesignSystem",):
        _purge_api_cache("design-system")


@receiver([post_save, post_delete])
def invalidate_feature_flags_cache(sender, instance, **kwargs):
    """Purge le cache quand un Feature Flag change."""
    if sender.__name__ in ("FeatureFlag",):
        _purge_api_cache("feature-flags")


@receiver([post_save, post_delete])
def invalidate_catalog_cache(sender, instance, **kwargs):
    """Purge le cache quand un produit ou une catégorie change."""
    if sender.__name__ in ("Product", "ProductVariant", "Category", "Brand"):
        _purge_api_cache("catalog")


@receiver([post_save, post_delete])
def invalidate_blog_cache(sender, instance, **kwargs):
    """Purge le cache quand un article ou une catégorie de blog change."""
    if sender.__name__ in ("Post", "BlogCategory", "BlogTag", "Comment"):
        _purge_api_cache("blog")


def _purge_api_cache(prefix):
    """
    Purge le cache Redis pour toutes les URLs commençant par
    /api/v1/{prefix}/. Comme Django ne permet pas une purge par préfixe
    nativement, on utilise une clé « version » qu'on incrémente.
    """
    try:
        key = f"cache_version:{prefix}"
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=None)
    except Exception:
        pass
'''


# ============================================================
#  FONCTIONS
# ============================================================

def patch_middleware():
    """Réduit les durées dans le middleware."""
    if not os.path.exists(MIDDLEWARE_PATH):
        print(f"  [ERREUR] {MIDDLEWARE_PATH} introuvable")
        return False

    with open(MIDDLEWARE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérifier si déjà modifié
    if "(r\"^/api/v1/navigation/\", 30)" in content:
        print("  [SKIP] middleware.py déjà corrigé")
        return True

    # Trouver le bloc PUBLIC_CACHE actuel
    pattern = re.compile(
        r'(\s*# Endpoints publics cacheables.*?PUBLIC_CACHE = \[.*?\])',
        re.DOTALL,
    )
    match = pattern.search(content)

    if not match:
        print("  [ATTENTION] Bloc PUBLIC_CACHE introuvable")
        print("  → Vérifiez apps/core/middleware.py manuellement")
        return False

    shutil.copy2(MIDDLEWARE_PATH, MIDDLEWARE_PATH + ".bak")
    content = content[:match.start(1)] + NEW_CACHE_CONFIG + content[match.end(1):]

    with open(MIDDLEWARE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] middleware.py : durées de cache réduites")
    return True


def create_signals():
    """Crée le fichier signals.py."""
    signals_path = os.path.join(BASE_DIR, "apps", "core", "signals.py")
    
    if os.path.exists(signals_path):
        with open(signals_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "invalidate_navigation_cache" in existing:
            print("  [SKIP] signals.py déjà configuré")
            return True
        shutil.copy2(signals_path, signals_path + ".bak")
        content = existing.rstrip() + "\n\n" + CACHE_SIGNALS
    else:
        content = CACHE_SIGNALS

    with open(signals_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] apps/core/signals.py créé")
    return True


def patch_apps_py():
    """Importe signals dans apps.py pour l'activer."""
    apps_path = os.path.join(BASE_DIR, "apps", "core", "apps.py")
    
    if not os.path.exists(apps_path):
        print(f"  [INFO] apps.py non trouvé, création...")
        content = '''from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from . import signals  # noqa
'''
        with open(apps_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] apps.py créé avec ready()")
        return True

    with open(apps_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "from . import signals" in content:
        print("  [SKIP] apps.py déjà configuré")
        return True

    shutil.copy2(apps_path, apps_path + ".bak")

    if "def ready(self)" in content:
        # Ajouter l'import dans ready()
        content = re.sub(
            r'def ready\(self\):\s*\n',
            'def ready(self):\n        from . import signals  # noqa\n',
            content,
        )
    else:
        # Ajouter la méthode ready
        content = content.rstrip() + '\n\n    def ready(self):\n        from . import signals  # noqa\n'

    with open(apps_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] apps.py patché")
    return True


def patch_settings():
    """S'assure que l'app est bien déclarée."""
    settings_path = os.path.join(BASE_DIR, "config", "settings.py")
    if not os.path.exists(settings_path):
        return False

    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # L'apps.core est déjà déclarée dans LOCAL_APPS, on vérifie juste
    if '"apps.core"' in content:
        print("  [OK] apps.core déjà dans INSTALLED_APPS")
        return True

    print("  [ATTENTION] apps.core absent de INSTALLED_APPS")
    return False


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  FIX DES DURÉES DE CACHE")
    print("=" * 60)

    print("\n[1/4] Réduction des durées de cache dans middleware.py...")
    patch_middleware()

    print("\n[2/4] Création des signaux de purge...")
    create_signals()

    print("\n[3/4] Activation des signaux dans apps.py...")
    patch_apps_py()

    print("\n[4/4] Vérification de settings.py...")
    patch_settings()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Testez en local : python manage.py check")
    print("  2. Ouvrez GitHub Desktop")
    print("  3. Summary : fix: reduce cache durations + auto-purge signals")
    print("  4. Commit to main → Push origin")
    print("  5. Attendez Railway (~3 min)")
    print()
    print("🎯 RÉSULTAT APRÈS DÉPLOIEMENT :")
    print("  → Les modifications de menus apparaissent en ~30 secondes")
    print("  → Le cache se purge automatiquement à chaque sauvegarde")


if __name__ == "__main__":
    main()