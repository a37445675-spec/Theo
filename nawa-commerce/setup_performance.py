"""
Phase 12.2 — Performance.
- Backend : cache Redis sur les API publiques + middleware
- Frontend : lazy loading, code splitting

Usage : python setup_performance.py
"""
import os
import re
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "apps")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "nawa-shop-frontend", "src")


# ============================================================
#              BACKEND — CACHE MIDDLEWARE
# ============================================================

CACHE_MIDDLEWARE = '''"""
Middleware de cache HTTP pour les endpoints publics.
Ajoute des headers Cache-Control aux réponses API publiques.
"""
from django.utils.deprecation import MiddlewareMixin


class CacheControlMiddleware(MiddlewareMixin):
    """
    Ajoute des headers Cache-Control sur les réponses API.
    Différencie les endpoints publics (cacheables) des privés (non cacheables).
    """

    # Endpoints publics cacheables (regex, durée en secondes)
    PUBLIC_CACHE = [
        (r"^/api/v1/design-system/", 3600),         # 1 heure
        (r"^/api/v1/navigation/", 1800),            # 30 minutes
        (r"^/api/v1/translations/", 3600),          # 1 heure
        (r"^/api/v1/feature-flags/", 300),          # 5 minutes
        (r"^/api/v1/announcements/", 300),          # 5 minutes
        (r"^/api/v1/media-library/", 1800),         # 30 minutes
        (r"^/api/v1/catalog/categories/", 1800),    # 30 minutes
        (r"^/api/v1/catalog/products/", 300),       # 5 minutes
        (r"^/api/v1/blog/categories/", 1800),       # 30 minutes
        (r"^/api/v1/blog/tags/", 1800),             # 30 minutes
        (r"^/api/v1/blog/posts/", 300),             # 5 minutes
        (r"^/api/v1/seo/", 3600),                   # 1 heure
        (r"^/api/v1/redirects/", 3600),             # 1 heure
    ]

    # Endpoints jamais cacheables
    PRIVATE_ENDPOINTS = [
        r"^/api/v1/auth/",
        r"^/api/v1/cart/",
        r"^/api/v1/checkout/",
        r"^/api/v1/orders/",
        r"^/api/v1/accounts/",
        r"^/api/v1/cms/",
        r"^/api/v1/forms/",
        r"^/admin/",
    ]

    def process_response(self, request, response):
        path = request.path

        # Ne pas toucher aux endpoints privés
        for pattern in self.PRIVATE_ENDPOINTS:
            if re.match(pattern, path):
                response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
                return response

        # Cache uniquement les GET réussis
        if request.method != "GET" or response.status_code >= 400:
            response["Cache-Control"] = "no-store"
            return response

        # Endpoints publics cacheables
        for pattern, duration in self.PUBLIC_CACHE:
            if re.match(pattern, path):
                response["Cache-Control"] = f"public, max-age={duration}, stale-while-revalidate={duration * 2}"
                response["Vary"] = "Accept, Accept-Language, Origin"
                return response

        # Par défaut : cache court
        response["Cache-Control"] = "public, max-age=60"
        return response
'''


# ============================================================
#              BACKEND — VUES AVEC CACHE
# ============================================================

def patch_catalog_views():
    """Ajoute le cache sur le catalogue."""
    views_path = os.path.join(SRC_DIR, "catalog", "views.py")
    if not os.path.exists(views_path):
        print("  [SKIP] apps/catalog/views.py introuvable")
        return

    with open(views_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "cache_page" in content:
        print("  [SKIP] Cache déjà configuré dans catalog/views.py")
        return

    # Ajouter l'import
    if "from django.utils.decorators import method_decorator" not in content:
        content = content.replace(
            "from rest_framework import",
            "from django.utils.decorators import method_decorator\nfrom django.views.decorators.cache import cache_page\nfrom rest_framework import",
            1,
        )

    # Ajouter le décorateur sur les actions list/retrieve
    # Utiliser @method_decorator au niveau classe
    pattern = r'(class ProductViewSet\([^)]+\):\s*\n)'
    match = re.search(pattern, content)
    if match and "method_decorator(cache_page" not in content:
        content = re.sub(
            pattern,
            r'\1    @method_decorator(cache_page(60 * 5), name="list")\n    @method_decorator(cache_page(60 * 5), name="retrieve")\n',
            content,
            count=1,
        )

    pattern = r'(class CategoryViewSet\([^)]+\):\s*\n)'
    match = re.search(pattern, content)
    if match and "method_decorator(cache_page" not in content:
        content = re.sub(
            pattern,
            r'\1    @method_decorator(cache_page(60 * 30), name="list")\n    @method_decorator(cache_page(60 * 30), name="retrieve")\n',
            content,
            count=1,
        )

    shutil.copy2(views_path, views_path + ".bak")
    with open(views_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] apps/catalog/views.py : cache ajouté")


def patch_blog_views():
    """Ajoute le cache sur le blog."""
    views_path = os.path.join(SRC_DIR, "blog", "views.py")
    if not os.path.exists(views_path):
        print("  [SKIP] apps/blog/views.py introuvable")
        return

    with open(views_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "cache_page" in content:
        print("  [SKIP] Cache déjà configuré dans blog/views.py")
        return

    if "from django.utils.decorators import method_decorator" not in content:
        content = "from django.utils.decorators import method_decorator\nfrom django.views.decorators.cache import cache_page\n" + content

    pattern = r'(class PostViewSet\([^)]+\):\s*\n)'
    content = re.sub(
        pattern,
        r'\1    @method_decorator(cache_page(60 * 5), name="list")\n    @method_decorator(cache_page(60 * 5), name="retrieve")\n',
        content,
        count=1,
    )

    pattern = r'(class BlogCategoryViewSet\([^)]+\):\s*\n)'
    content = re.sub(
        pattern,
        r'\1    @method_decorator(cache_page(60 * 30), name="list")\n',
        content,
        count=1,
    )

    shutil.copy2(views_path, views_path + ".bak")
    with open(views_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] apps/blog/views.py : cache ajouté")


def patch_settings_performance():
    """Ajoute le middleware et la config cache au settings."""
    settings_path = os.path.join(BASE_DIR, "config", "settings.py")
    if not os.path.exists(settings_path):
        print("  [SKIP] settings.py introuvable")
        return

    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "CacheControlMiddleware" in content:
        print("  [SKIP] Middleware déjà configuré")
        return

    # Ajouter le middleware après CorsMiddleware
    middleware_pattern = r'("corsheaders\.middleware\.CorsMiddleware",\n)'
    if middleware_pattern in content:
        content = re.sub(
            middleware_pattern,
            r'\1    "apps.core.middleware.CacheControlMiddleware",\n',
            content,
        )
    else:
        # Fallback : ajouter après CommonMiddleware
        content = content.replace(
            '"django.middleware.common.CommonMiddleware",',
            '"django.middleware.common.CommonMiddleware",\n    "apps.core.middleware.CacheControlMiddleware",',
            1,
        )

    shutil.copy2(settings_path, settings_path + ".before-perf.bak")
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] config/settings.py : middleware ajouté")


def write_middleware():
    """Crée le middleware de cache."""
    path = os.path.join(SRC_DIR, "core", "middleware.py")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if "CacheControlMiddleware" in existing:
            print("  [SKIP] Middleware existe déjà")
            return
        content = existing + "\n\n" + CACHE_MIDDLEWARE
    else:
        content = CACHE_MIDDLEWARE

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] apps/core/middleware.py")


# ============================================================
#              FRONTEND — LAZY LOADING
# ============================================================

def patch_frontend_app():
    """Ajoute lazy loading sur les pages admin."""
    app_path = os.path.join(FRONTEND_DIR, "App.jsx")
    if not os.path.exists(app_path):
        print("  [SKIP] App.jsx introuvable")
        return

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "React.lazy" in content or "lazy(" in content:
        print("  [SKIP] Lazy déjà configuré")
        return

    # Remplacer les imports admin par des lazy imports
    content = content.replace(
        'import AdminPagesList from "./pages/admin/AdminPagesList.jsx";',
        'const AdminPagesList = lazy(() => import("./pages/admin/AdminPagesList.jsx"));',
    )
    content = content.replace(
        'import PageBuilder from "./pages/admin/PageBuilder.jsx";',
        'const PageBuilder = lazy(() => import("./pages/admin/PageBuilder.jsx"));',
    )

    # Ajouter lazy + Suspense à l'import React
    content = content.replace(
        'import { useEffect } from "react";',
        'import { useEffect, lazy, Suspense } from "react";',
    )

    # Envelopper les routes admin dans Suspense
    content = content.replace(
        '<Route path="/admin/pages" element={<AdminPagesList />} />',
        '<Route path="/admin/pages" element={<Suspense fallback={<div style={{padding: "3rem", textAlign: "center"}}>Chargement...</div>}><AdminPagesList /></Suspense>} />',
    )
    content = content.replace(
        '<Route path="/admin/pages/:pageId/builder" element={<PageBuilder />} />',
        '<Route path="/admin/pages/:pageId/builder" element={<Suspense fallback={<div style={{padding: "3rem", textAlign: "center"}}>Chargement de l\'éditeur...</div>}><PageBuilder /></Suspense>} />',
    )

    shutil.copy2(app_path, app_path + ".before-perf.bak")
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] App.jsx : lazy loading admin ajouté")


def patch_vite_config():
    """Ajoute les optimisations Vite."""
    vite_path = os.path.join(os.path.dirname(FRONTEND_DIR), "vite.config.js")
    if not os.path.exists(vite_path):
        print("  [SKIP] vite.config.js introuvable")
        return

    with open(vite_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "manualChunks" in content:
        print("  [SKIP] Vite déjà optimisé")
        return

    # Ajouter les optimisations au build
    build_block = '''
  build: {
    outDir: "dist",
    sourcemap: false,
    minify: "esbuild",
    target: "es2020",
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"],
          "puck-vendor": ["@puckeditor/core"],
          "vendor": ["axios"],
        },
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash].[ext]",
      },
    },
    cssCodeSplit: true,
    assetsInlineLimit: 4096,
  },

  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom", "axios"],
  },
'''

    # Insérer avant la dernière } de defineConfig
    last_brace = content.rfind("}")
    content = content[:last_brace] + build_block + "\n" + content[last_brace:]

    shutil.copy2(vite_path, vite_path + ".bak")
    with open(vite_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] vite.config.js : optimisations build ajoutées")


# ============================================================
#              MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 12.2 — PERFORMANCE")
    print("=" * 60)

    print("\n[BACKEND]")
    print("\n[1/4] Création du middleware de cache...")
    write_middleware()

    print("\n[2/4] Cache sur catalog/views.py...")
    patch_catalog_views()

    print("\n[3/4] Cache sur blog/views.py...")
    patch_blog_views()

    print("\n[4/4] Configuration du middleware dans settings...")
    patch_settings_performance()

    print("\n[FRONTEND]")
    if os.path.exists(FRONTEND_DIR):
        print("\n[1/2] Lazy loading dans App.jsx...")
        patch_frontend_app()

        print("\n[2/2] Optimisations Vite...")
        patch_vite_config()
    else:
        print(f"\n  [INFO] Frontend introuvable à {FRONTEND_DIR}")
        print("  → Modifiez le chemin FRONTEND_DIR dans le script")

    print()
    print("=" * 60)
    print("  ✅ PHASE 12.2 TERMINÉE")
    print("=" * 60)
    print("\nBackups créés :")
    print("  apps/catalog/views.py.bak")
    print("  apps/blog/views.py.bak")
    print("  config/settings.py.before-perf.bak")
    print("  src/App.jsx.before-perf.bak")
    print("  vite.config.js.bak")
    print()
    print("⚠️  Ajoutez dans .env.production :")
    print("  USE_REDIS=False   (dev)  ou  True (prod)")


if __name__ == "__main__":
    main()