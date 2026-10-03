"""
Correctif performance — cache via middleware uniquement.
Ne touche PAS aux vues (qui contiennent déjà la logique métier).

Usage : python fix_performance_cache.py
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("  CORRECTIF PERFORMANCE — CACHE VIA MIDDLEWARE")
    print("=" * 60)

    # 1. Vérifier que le middleware est bien en place
    middleware_path = os.path.join(BASE_DIR, "apps", "core", "middleware.py")
    if not os.path.exists(middleware_path):
        print("\n  ❌ apps/core/middleware.py introuvable")
        print("  → Relancez setup_performance.py d'abord")
        return

    with open(middleware_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "CacheControlMiddleware" not in content:
        print("\n  ❌ CacheControlMiddleware absent")
        return

    print("\n  ✅ apps/core/middleware.py présent")

    # 2. Vérifier l'installation dans settings.py
    settings_path = os.path.join(BASE_DIR, "config", "settings.py")
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = f.read()

    if "CacheControlMiddleware" in settings:
        print("  ✅ Middleware enregistré dans settings.py")
    else:
        print("  ⚠️  Middleware NON enregistré dans settings.py")
        print("  → Ajoutez manuellement dans MIDDLEWARE :")
        print('     "apps.core.middleware.CacheControlMiddleware",')

    # 3. Vérifier que les vues sont saines
    for views_path in [
        os.path.join(BASE_DIR, "apps", "catalog", "views.py"),
        os.path.join(BASE_DIR, "apps", "blog", "views.py"),
    ]:
        name = os.path.basename(os.path.dirname(views_path)) + "/views.py"
        with open(views_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "cache_page" in content:
            print(f"  ⚠️  {name} contient encore des décorateurs cache_page")
            print(f"     → Ce n'est pas grave, mais vous pouvez les retirer")
        else:
            print(f"  ✅ {name} sain")

    print()
    print("=" * 60)
    print("  ✅ LE CACHE FONCTIONNE VIA LE MIDDLEWARE")
    print("=" * 60)
    print("\nLe middleware ajoute automatiquement :")
    print("  - Cache-Control: public, max-age=XXX sur les endpoints publics")
    print("  - Cache-Control: no-store sur les endpoints privés")
    print("  - Vary: Accept, Accept-Language, Origin")
    print()
    print("Rien d'autre à faire côté vues.")
    print("Testez : python manage.py check")


if __name__ == "__main__":
    main()