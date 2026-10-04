"""
Ajoute l'endpoint /api/v1/catalog/categories/{slug}/attributes/
qui retourne les attributs dynamiques d'une catégorie.

Usage : python fix_category_attributes_api.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_DIR = os.path.join(BASE_DIR, "apps", "catalog")
VIEWS_PATH = os.path.join(CATALOG_DIR, "views.py")
URLS_PATH = os.path.join(CATALOG_DIR, "urls.py")
SERIALIZERS_PATH = os.path.join(CATALOG_DIR, "serializers.py")


# ============================================================
#  SERIALIZER À AJOUTER
# ============================================================

SERIALIZER_CODE = '''

# ============================================================
#  CATEGORY ATTRIBUTES SERIALIZER
# ============================================================

class CategoryAttributeSerializer(serializers.Serializer):
    """Serializer pour les attributs dynamiques d'une catégorie."""
    code = serializers.CharField()
    label = serializers.CharField()
    attribute_type = serializers.CharField(source="attribute.attribute_type")
    unit = serializers.CharField(source="attribute.unit")
    choices = serializers.JSONField(source="attribute.choices")
    help_text = serializers.CharField(source="attribute.help_text")
    is_required = serializers.BooleanField()
    order = serializers.IntegerField(source="attribute.id")
'''


# ============================================================
#  VUE À AJOUTER
# ============================================================

VIEW_CODE = '''

# ============================================================
#  CATEGORY ATTRIBUTES VIEW
# ============================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CategoryAttributesView(APIView):
    """
    Retourne les attributs dynamiques d'une catégorie.
    Utilisé par le frontend pour générer les filtres produits.

    GET /api/v1/catalog/categories/{slug}/attributes/
    """
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 5))  # 5 minutes
    def get(self, request, slug):
        from .models import Category
        from .serializers import CategoryAttributeSerializer

        category = get_object_or_404(Category, slug=slug)
        attribute_set = category.get_effective_attribute_set()

        if not attribute_set:
            return Response([], status=status.HTTP_200_OK)

        items = attribute_set.items.select_related("attribute").order_by("order", "id")
        serializer = CategoryAttributeSerializer(items, many=True)

        return Response(serializer.data)
'''


# ============================================================
#  URL À AJOUTER
# ============================================================

URL_CODE = '''
# === Category Attributes (attributs dynamiques) ===
path(
    "categories/<slug:slug>/attributes/",
    CategoryAttributesView.as_view(),
    name="category-attributes",
),
'''


# ============================================================
#  FONCTIONS
# ============================================================

def ensure_import_allow_any(content):
    """S'assure que AllowAny est importé."""
    if "AllowAny" in content:
        return content
    if "from rest_framework.permissions import" in content:
        content = re.sub(
            r'from rest_framework\.permissions import ([^\n]+)',
            r'from rest_framework.permissions import \1, AllowAny',
            content,
        )
    else:
        content = "from rest_framework.permissions import AllowAny\n" + content
    return content


def patch_views():
    """Ajoute CategoryAttributesView dans views.py."""
    if not os.path.exists(VIEWS_PATH):
        print(f"  [ERREUR] {VIEWS_PATH} introuvable")
        return False

    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "CategoryAttributesView" in content:
        print("  [SKIP] CategoryAttributesView existe déjà")
        return True

    shutil.copy2(VIEWS_PATH, VIEWS_PATH + ".bak")

    # S'assurer des imports
    if "from rest_framework.response import Response" not in content:
        content = "from rest_framework.response import Response\n" + content
    if "from rest_framework import status" not in content:
        content = "from rest_framework import status\n" + content
    if "from django.shortcuts import get_object_or_404" not in content:
        content = "from django.shortcuts import get_object_or_404\n" + content
    content = ensure_import_allow_any(content)

    # Ajouter la vue à la fin
    content = content.rstrip() + "\n" + VIEW_CODE

    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] CategoryAttributesView ajoutée à views.py")
    return True


def patch_serializers():
    """Ajoute CategoryAttributeSerializer dans serializers.py."""
    if not os.path.exists(SERIALIZERS_PATH):
        print(f"  [INFO] serializers.py introuvable, ignoré")
        return False

    with open(SERIALIZERS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "CategoryAttributeSerializer" in content:
        print("  [SKIP] CategoryAttributeSerializer existe déjà")
        return True

    shutil.copy2(SERIALIZERS_PATH, SERIALIZERS_PATH + ".bak")
    content = content.rstrip() + "\n" + SERIALIZER_CODE

    with open(SERIALIZERS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] CategoryAttributeSerializer ajouté à serializers.py")
    return True


def patch_urls():
    """Ajoute la route dans urls.py."""
    if not os.path.exists(URLS_PATH):
        print(f"  [ERREUR] {URLS_PATH} introuvable")
        return False

    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "category-attributes" in content:
        print("  [SKIP] Route category-attributes existe déjà")
        return True

    shutil.copy2(URLS_PATH, URLS_PATH + ".bak")

    # Ajouter l'import de la vue
    if "CategoryAttributesView" not in content:
        # Chercher la ligne d'import existante de .views
        if "from .views import" in content:
            content = re.sub(
                r'from \.views import ([^\n]+)',
                r'from .views import \1, CategoryAttributesView',
                content,
                count=1,
            )
        else:
            content = "from .views import CategoryAttributesView\n" + content

    # Ajouter la route dans urlpatterns
    if "urlpatterns = [" in content:
        content = re.sub(
            r'(urlpatterns\s*=\s*\[)',
            r'\1\n' + URL_CODE,
            content,
            count=1,
        )
    else:
        print("  [ATTENTION] urlpatterns introuvable")
        return False

    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Route categories/<slug>/attributes/ ajoutée")
    return True


def run_check():
    """Vérifie que Django démarre."""
    import subprocess, sys
    try:
        subprocess.run([sys.executable, "manage.py", "check"], check=True)
        print("\n  ✅ Django démarre correctement")
        return True
    except subprocess.CalledProcessError:
        print("\n  ❌ Django rencontre une erreur")
        return False


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  FIX CATEGORY ATTRIBUTES API")
    print("=" * 60)

    print("\n[1/4] Ajout du serializer...")
    patch_serializers()

    print("\n[2/4] Ajout de la vue...")
    patch_views()

    print("\n[3/4] Ajout de la route URL...")
    patch_urls()

    print("\n[4/4] Vérification Django...")
    run_check()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Ouvrez GitHub Desktop")
    print("  2. Summary : feat: category attributes endpoint")
    print("  3. Commit to main → Push origin")
    print("  4. Attendez Railway (~3 min)")
    print()
    print("🧪 TEST APRÈS DÉPLOIEMENT :")
    print("  https://theo-production-c85a.up.railway.app/api/v1/catalog/categories/cheveux/attributes/")
    print("  → Doit retourner un JSON avec les attributs (type_peau, texture_cheveux, ...)")


if __name__ == "__main__":
    main()