"""
Phase 7 — Vérification intégrale.
Contrôle que tous les éléments sont en place.

Usage : python verify_phase7.py
"""
import os
import subprocess
import sys

BACKEND = os.path.join("nawa-commerce")
FRONTEND = os.path.join("nawa-shop-frontend")


CHECKS = [
    # Backend
    (BACKEND, "apps/cms/models.py", "class Widget(models.Model)", "Modèle Widget"),
    (BACKEND, "apps/cms/models.py", "class ReusableSection(models.Model)", "Modèle ReusableSection"),
    (BACKEND, "apps/cms/widget_serializers.py", "class WidgetSerializer", "Serializer Widget"),
    (BACKEND, "apps/cms/widget_views.py", "class WidgetViewSet", "ViewSet Widget"),
    (BACKEND, "apps/cms/widget_urls.py", "router.register", "URLs Widget"),
    (BACKEND, "apps/cms/widget_admin.py", "@admin.register(Widget)", "Admin Widget"),
    # Frontend
    (FRONTEND, "src/puck/config.jsx", "export const puckConfig", "Config Puck"),
    (FRONTEND, "src/pages/admin/PageBuilder.jsx", "export default function PageBuilder", "PageBuilder"),
    (FRONTEND, "src/pages/admin/AdminPagesList.jsx", "export default function AdminPagesList", "Liste admin"),
    (FRONTEND, "src/components/PublicPageRenderer.jsx", "export default function PublicPageRenderer", "PublicPageRenderer"),
    # Routes dans App.jsx
    (FRONTEND, "src/App.jsx", "AdminPagesList", "Route AdminPagesList"),
    (FRONTEND, "src/App.jsx", "PageBuilder", "Route PageBuilder"),
]


def check_file(base, rel_path, needle, label):
    full_path = os.path.join(base, rel_path)
    if not os.path.exists(full_path):
        return False, f"[MANQUANT] {rel_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        if needle in f.read():
            return True, f"[OK] {label}"
        return False, f"[INCOMPLET] {label} ({rel_path})"


def main():
    print("=" * 60)
    print("  VÉRIFICATION PHASE 7")
    print("=" * 60)

    all_ok = True
    for base, rel, needle, label in CHECKS:
        ok, msg = check_file(base, rel, needle, label)
        print(f"  {msg}")
        all_ok &= ok

    # Vérifier les dépendances npm
    pkg = os.path.join(FRONTEND, "package.json")
    if os.path.exists(pkg):
        with open(pkg, "r", encoding="utf-8") as f:
            if "@puckeditor/core" in f.read():
                print("  [OK] @puckeditor/core installé")
            else:
                print("  [MANQUANT] @puckeditor/core — lancez npm install @puckeditor/core")
                all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("  ✅ PHASE 7 VALIDÉE")
        print("=" * 60)
        print("\n🚀 Lancez les serveurs :")
        print(f"  cd {BACKEND} && python manage.py runserver")
        print(f"  cd {FRONTEND} && npm run dev")
        print("\n🧪 Test :")
        print("  1. http://localhost:8000/admin/cms/widget/ (ajoutez 2-3 widgets)")
        print("  2. http://localhost:5173/admin/pages")
        print("  3. Cliquez Éditer → drag-and-drop dans Puck")
        print("  4. Publier → sauvegarde automatique en base")
        print("  5. Consultez http://localhost:8000/api/v1/cms/widgets/?page=1")
    else:
        print("  ⚠️  PHASE 7 INCOMPLÈTE")
        print("=" * 60)
        print("\nCorrigez les éléments manquants puis relancez ce script.")


if __name__ == "__main__":
    main()
