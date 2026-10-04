"""
Vérifie et corrige les routes Puck dans App.jsx.

Usage : python fix_puck_routes.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
APP_PATH = os.path.join(SRC_DIR, "App.jsx")
ADMIN_DIR = os.path.join(SRC_DIR, "pages", "admin")


def main():
    print("=" * 60)
    print("  DIAGNOSTIC DES ROUTES PUCK")
    print("=" * 60)

    if not os.path.exists(APP_PATH):
        print(f"  ❌ App.jsx introuvable")
        return

    # 1. Vérifier les fichiers
    print("\n[1/3] Vérification des fichiers...")
    files = {
        "AdminPagesList.jsx": os.path.join(ADMIN_DIR, "AdminPagesList.jsx"),
        "PageBuilder.jsx": os.path.join(ADMIN_DIR, "PageBuilder.jsx"),
    }
    for name, path in files.items():
        status = "✅" if os.path.exists(path) else "❌"
        print(f"  {status} {name}")

    # 2. Vérifier les imports et routes dans App.jsx
    print("\n[2/3] Analyse de App.jsx...")
    with open(APP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    has_import_pages = "AdminPagesList" in content
    has_import_builder = "PageBuilder" in content
    has_route_pages = 'path="/admin/pages"' in content
    has_route_builder = 'path="/admin/pages/:pageId/builder"' in content

    print(f"  Import AdminPagesList : {'✅' if has_import_pages else '❌'}")
    print(f"  Import PageBuilder    : {'✅' if has_import_builder else '❌'}")
    print(f"  Route /admin/pages    : {'✅' if has_route_pages else '❌'}")
    print(f"  Route /admin/pages/:id/builder : {'✅' if has_route_builder else '❌'}")

    if has_import_pages and has_import_builder and has_route_pages and has_route_builder:
        print("\n  ✅ Toutes les routes sont présentes localement.")
        print("  → Il faut peut-être commit + push sur GitHub.")
        return

    # 3. Correction automatique
    print("\n[3/3] Correction automatique...")
    shutil.copy2(APP_PATH, APP_PATH + ".bak")

    # Ajouter les imports
    if not has_import_pages or not has_import_builder:
        imports = (
            'import AdminPagesList from "./pages/admin/AdminPagesList.jsx";\n'
            'import PageBuilder from "./pages/admin/PageBuilder.jsx";\n'
        )
        marker = 'import Home from "./pages/Home'
        if marker in content:
            content = content.replace(marker, imports + marker, 1)
        else:
            first_import = re.search(r'^(import\s+.*\n)', content, re.MULTILINE)
            if first_import:
                content = content[:first_import.end()] + imports + content[first_import.end():]
        print("  [OK] Imports ajoutés")

    # Ajouter les routes
    if not has_route_pages or not has_route_builder:
        routes = '''                            {/* ---- Admin : Page Builder ---- */}
                            <Route path="/admin/pages" element={<AdminPagesList />} />
                            <Route path="/admin/pages/:pageId/builder" element={<PageBuilder />} />

'''
        marker = '<Route path="*" element={<NotFound />} />'
        if marker in content:
            content = content.replace(marker, routes + "                            " + marker)
            print("  [OK] Routes ajoutées")
        else:
            print("  [ATTENTION] NotFound marker introuvable")
            print("  → Ajoutez les routes manuellement")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + "=" * 60)
    print("  ✅ CORRECTION TERMINÉE")
    print("=" * 60)
    print("\n📋 Prochaines étapes :")
    print("  1. Ouvrez GitHub Desktop")
    print("  2. Summary : fix: add Puck editor routes")
    print("  3. Commit to main → Push origin")
    print("  4. Attendez Railway (~3 min)")
    print("  5. Testez : sweet-communication.up.railway.app/admin/pages/1/builder")


if __name__ == "__main__":
    main()