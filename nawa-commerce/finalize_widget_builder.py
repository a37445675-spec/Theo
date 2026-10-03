"""
Finalisation du Widget Builder - Backend.
Corrige l'import, vérifie les modèles, applique les migrations, seed.

Usage : python finalize_widget_builder.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CMS_DIR = os.path.join(BASE_DIR, "apps", "cms")


# ============================================================
#                    ÉTAPES
# ============================================================

def step_fix_imports():
    """Corrige l'import dans widget_views.py et widget_urls.py."""
    print("\n[1/5] Correction des imports...")

    # widget_views.py
    path = os.path.join(CMS_DIR, "widget_views.py")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "from .serializers import WidgetSerializer" in content:
            shutil.copy2(path, path + ".bak")
            content = content.replace(
                "from .serializers import WidgetSerializer, ReusableSectionSerializer",
                "from .widget_serializers import WidgetSerializer, ReusableSectionSerializer"
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print("  [OK] widget_views.py corrigé")
        else:
            print("  [SKIP] widget_views.py déjà correct")

    # widget_serializers.py — s'assurer que le fichier existe
    path = os.path.join(CMS_DIR, "widget_serializers.py")
    if not os.path.exists(path):
        print("  [ERREUR] widget_serializers.py introuvable")
        print("  → Relancez d'abord inject_widget_builder_backend.py")
        return False
    print("  [OK] widget_serializers.py présent")
    return True


def step_check_models():
    """Vérifie que les modèles Widget et ReusableSection existent."""
    print("\n[2/5] Vérification des modèles...")

    path = os.path.join(CMS_DIR, "models.py")
    if not os.path.exists(path):
        print("  [ERREUR] models.py introuvable")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    has_widget = "class Widget(models.Model)" in content
    has_reusable = "class ReusableSection(models.Model)" in content

    if has_widget and has_reusable:
        print("  [OK] Widget + ReusableSection présents")
        return True

    print(f"  [ATTENTION] Widget={'OK' if has_widget else 'MANQUANT'}, "
          f"ReusableSection={'OK' if has_reusable else 'MANQUANT'}")
    print("  → Vérifiez apps/cms/models.py manuellement")
    return False


def step_fix_admin():
    """S'assure que widget_admin est bien importé dans admin.py."""
    print("\n[3/5] Vérification de l'admin...")

    admin_path = os.path.join(CMS_DIR, "admin.py")
    widget_admin_path = os.path.join(CMS_DIR, "widget_admin.py")

    if not os.path.exists(widget_admin_path):
        print("  [ERREUR] widget_admin.py introuvable")
        return False

    if not os.path.exists(admin_path):
        print("  [ATTENTION] admin.py introuvable")
        return False

    with open(admin_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "from . import widget_admin" in content or "widget_admin" in content:
        print("  [OK] widget_admin importé")
        return True

    shutil.copy2(admin_path, admin_path + ".bak")
    with open(admin_path, "a", encoding="utf-8") as f:
        f.write("\n\n# === Widget Builder ===\nfrom . import widget_admin  # noqa: F401,E402\n")
    print("  [OK] widget_admin importé dans admin.py")
    return True


def step_check_urls():
    """Vérifie que la route Widget Builder est bien dans urls.py."""
    print("\n[4/5] Vérification de urls.py...")

    urls_path = None
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
    ]:
        if os.path.exists(c):
            urls_path = c
            break

    if not urls_path:
        print("  [ERREUR] urls.py introuvable")
        return False

    with open(urls_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.cms.widget_urls" not in content:
        print("  [ATTENTION] route widget_urls absente")
        return False

    # Vérifier l'ordre : widget_urls DOIT être AVANT cms.urls générales
    idx_widget = content.find("apps.cms.widget_urls")
    idx_cms = content.find('include("apps.cms.urls")')
    if idx_cms != -1 and idx_cms < idx_widget:
        print("  [ATTENTION] widget_urls doit être AVANT cms.urls pour primer")
        print(f"  → Réordonnez dans {os.path.relpath(urls_path, BASE_DIR)}")
        return False

    print("  [OK] route Widget Builder présente et prioritaire")
    return True


def step_migrate_and_seed():
    """Lance makemigrations, migrate et le seed."""
    print("\n[5/5] Migrations + seed...")

    try:
        subprocess.run(
            [sys.executable, "manage.py", "makemigrations", "cms"],
            check=True
        )
        print("  [OK] makemigrations cms")

        subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            check=True
        )
        print("  [OK] migrate")

        subprocess.run(
            [sys.executable, "manage.py", "seed_page_builder"],
            check=True
        )
        print("  [OK] seed_page_builder")
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        return False
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  FINALISATION WIDGET BUILDER - BACKEND")
    print("=" * 60)

    ok = True
    ok &= step_fix_imports()
    ok &= step_check_models()
    ok &= step_fix_admin()
    ok &= step_check_urls()

    if not ok:
        print("\n" + "!" * 60)
        print("  Des prérequis manquent.")
        print("  Relancez inject_widget_builder_backend.py si nécessaire.")
        print("!" * 60)
        return

    ok &= step_migrate_and_seed()

    print("\n" + "=" * 60)
    if ok:
        print("  ✅ PHASE 7 — BACKEND FINALISÉ")
    else:
        print("  ⚠️  TERMINÉ AVEC ERREURS")
    print("=" * 60)
    print("\nEndpoints :")
    print("  Arbre d'une page : GET /api/v1/cms/widgets/?page=1")
    print("  Save tree        : POST /api/v1/cms/widgets/save-tree/")
    print("  Duplicate        : POST /api/v1/cms/widgets/{id}/duplicate/")
    print("  Sections réutil. : GET /api/v1/cms/reusable-sections/")


if __name__ == "__main__":
    main()