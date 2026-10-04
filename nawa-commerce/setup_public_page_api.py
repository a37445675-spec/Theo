"""
Crée un endpoint public pour les widgets d'une page.
Résout l'erreur 401 sur /pages/:id

Usage : python setup_public_page_api.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CMS_DIR = os.path.join(BASE_DIR, "apps", "cms")
VIEWS_PATH = os.path.join(CMS_DIR, "widget_views.py")
URLS_PATH = os.path.join(CMS_DIR, "widget_urls.py")


# ============================================================
#  CODE À AJOUTER
# ============================================================

PUBLIC_VIEW_CODE = '''

# ============================================================
#  ENDPOINT PUBLIC — Widgets d'une page (sans auth)
# ============================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def public_page_widgets(request, page_id):
    """
    Endpoint public : retourne les widgets d'une page.
    Accessible sans authentification pour afficher les pages publiques.

    GET /api/v1/cms/pages/{page_id}/public/
    """
    from .models import PageTemplate, Widget
    from .widget_serializers import WidgetSerializer

    try:
        page = PageTemplate.objects.get(pk=page_id)
    except PageTemplate.DoesNotExist:
        return Response(
            {"detail": "Page introuvable."},
            status=404,
        )

    # Seuls les widgets racine (parent=None)
    widgets = Widget.objects.filter(page=page, parent=None).order_by("order")

    # Filtrer les widgets non visibles
    widgets = [w for w in widgets if w.is_visible]

    serializer = WidgetSerializer(widgets, many=True, context={"request": request})
    return Response({
        "page": {
            "id": page.pk,
            "name": page.name,
            "template_type": page.template_type,
        },
        "widgets": serializer.data,
    })
'''


URLS_CODE = '''"""URLs pour le Widget Builder."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .widget_views import WidgetViewSet, ReusableSectionViewSet, public_page_widgets

router = DefaultRouter()
router.register(r"widgets", WidgetViewSet, basename="widget")
router.register(r"reusable-sections", ReusableSectionViewSet, basename="reusable-section")

urlpatterns = [
    # Endpoint public (sans auth) — AVANT les routes du router
    path("pages/<int:page_id>/public/", public_page_widgets, name="public-page-widgets"),
    path("", include(router.urls)),
]
'''


# ============================================================
#  FONCTIONS
# ============================================================

def ensure_imports(content):
    """Vérifie que les imports nécessaires sont présents."""
    needed = [
        ("from rest_framework.decorators import api_view, permission_classes", 
         "from rest_framework.decorators import action"),
        ("from rest_framework.permissions import AllowAny",
         "from rest_framework.permissions import IsAdminUser"),
    ]
    
    for import_line, reference in needed:
        if import_line in content:
            continue
        # Insérer avant la référence existante
        if reference in content:
            content = content.replace(reference, import_line + "\n" + reference, 1)
    
    return content


def patch_views():
    """Ajoute l'endpoint public dans widget_views.py."""
    if not os.path.exists(VIEWS_PATH):
        print(f"  [ERREUR] {VIEWS_PATH} introuvable")
        return False

    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "public_page_widgets" in content:
        print("  [SKIP] Endpoint public déjà présent")
        return False

    shutil.copy2(VIEWS_PATH, VIEWS_PATH + ".bak")

    # S'assurer que Response et status sont importés
    if "from rest_framework.response import Response" not in content:
        content = "from rest_framework.response import Response\n" + content

    # S'assurer que api_view et permission_classes sont importés
    if "api_view" not in content:
        content = "from rest_framework.decorators import api_view, permission_classes\n" + content

    if "AllowAny" not in content:
        content = "from rest_framework.permissions import AllowAny, IsAdminUser\n" + content

    # Ajouter le code à la fin
    content = content.rstrip() + "\n" + PUBLIC_VIEW_CODE

    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Endpoint public_page_widgets ajouté à widget_views.py")
    return True


def patch_urls():
    """Ajoute la route dans widget_urls.py."""
    if not os.path.exists(URLS_PATH):
        print(f"  [ERREUR] {URLS_PATH} introuvable")
        return False

    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "public_page_widgets" in content:
        print("  [SKIP] Route déjà présente")
        return False

    shutil.copy2(URLS_PATH, URLS_PATH + ".bak")
    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(URLS_CODE)
    print("  [OK] Route /pages/:id/public/ ajoutée à widget_urls.py")
    return True


def patch_puck_page():
    """Modifie PuckPage.jsx pour utiliser la nouvelle route."""
    FRONTEND = os.path.join(os.path.dirname(BASE_DIR), "nawa-shop-frontend", "src", "pages", "PuckPage.jsx")
    
    if not os.path.exists(FRONTEND):
        print(f"  [INFO] PuckPage.jsx non trouvé (frontend non modifié)")
        return False

    with open(FRONTEND, "r", encoding="utf-8") as f:
        content = f.read()

    if "pages/${pageId}/public" in content:
        print("  [SKIP] PuckPage.jsx déjà patché")
        return False

    shutil.copy2(FRONTEND, FRONTEND + ".bak")

    # Remplacer l'URL
    content = content.replace(
        'fetch(`/api/v1/cms/widgets/?page=${pageId}`)',
        'fetch(`/api/v1/cms/pages/${pageId}/public/`)'
    )

    # Adapter le parsing (l'API renvoie {page, widgets} au lieu d'un tableau)
    old_parsing = '''.then((widgets) => {
        const list = Array.isArray(widgets) ? widgets : widgets.results || [];
        setData({
          content: list.map(widgetToPuck),
          root: { props: {} },
        });
      })'''
    
    new_parsing = '''.then((response) => {
        // Nouvelle API : { page: {...}, widgets: [...] }
        const widgets = response.widgets || (Array.isArray(response) ? response : []);
        setData({
          content: widgets.map(widgetToPuck),
          root: { props: {} },
        });
      })'''

    if old_parsing in content:
        content = content.replace(old_parsing, new_parsing)
        print("  [OK] PuckPage.jsx adapté au nouveau format")
    else:
        print("  [ATTENTION] Structure de parsing non trouvée — vérifiez manuellement")

    with open(FRONTEND, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  SETUP ENDPOINT PUBLIC /api/v1/cms/pages/:id/public/")
    print("=" * 60)

    if not os.path.exists(CMS_DIR):
        print(f"\n  ❌ Dossier apps/cms/ introuvable")
        print("  → Êtes-vous à la racine de nawa-commerce ?")
        return

    print("\n[1/3] Ajout de l'endpoint public dans widget_views.py...")
    patch_views()

    print("\n[2/3] Ajout de la route dans widget_urls.py...")
    patch_urls()

    print("\n[3/3] Adaptation de PuckPage.jsx (frontend)...")
    patch_puck_page()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Vérifiez les fichiers modifiés dans VS Code")
    print("  2. Testez en local (optionnel) : python manage.py check")
    print("  3. Ouvrez GitHub Desktop")
    print("  4. Summary : feat: public page widgets endpoint")
    print("  5. Commit to main → Push origin")
    print("  6. Attendez Railway (~3 min)")
    print("  7. Testez : https://sweet-communication-production-1afa.up.railway.app/pages/1")


if __name__ == "__main__":
    main()