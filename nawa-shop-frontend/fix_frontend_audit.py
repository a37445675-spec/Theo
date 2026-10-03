"""
Corrige les 2 bugs détectés par l'audit frontend :
1. Imports de PageBuilder.jsx (../ → ../../)
2. Routes admin/pages manquantes dans App.jsx

Usage : python fix_frontend_audit.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
PAGE_BUILDER = os.path.join(SRC_DIR, "pages", "admin", "PageBuilder.jsx")
APP_PATH = os.path.join(SRC_DIR, "App.jsx")


# ============================================================
#              CORRECTIF 1 : IMPORTS PageBuilder
# ============================================================

def fix_page_builder_imports():
    print("[1/2] Correction des imports de PageBuilder.jsx...")

    if not os.path.exists(PAGE_BUILDER):
        print(f"  [ERREUR] {PAGE_BUILDER} introuvable")
        return False

    with open(PAGE_BUILDER, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Remplacer les imports cassés
    content = content.replace(
        'from "../puck/config"',
        'from "../../puck/config"',
    )
    content = content.replace(
        'from "../utils/api"',
        'from "../../utils/api"',
    )
    # Variantes
    content = content.replace(
        'from "../puck/config.jsx"',
        'from "../../puck/config.jsx"',
    )
    content = content.replace(
        'from "../utils/api.js"',
        'from "../../utils/api.js"',
    )

    if content == original:
        print("  [SKIP] Aucune modification nécessaire")
        return True

    # Backup
    shutil.copy2(PAGE_BUILDER, PAGE_BUILDER + ".bak")
    with open(PAGE_BUILDER, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  [OK] Imports corrigés dans PageBuilder.jsx")

    # Afficher les imports
    for line in content.split("\n"):
        if line.startswith("import") and ("puck" in line or "utils" in line):
            print(f"       {line.strip()[:80]}")
    return True


# ============================================================
#              CORRECTIF 2 : ROUTES App.jsx
# ============================================================

def fix_app_routes():
    print("\n[2/2] Ajout des routes admin/pages dans App.jsx...")

    if not os.path.exists(APP_PATH):
        print(f"  [ERREUR] {APP_PATH} introuvable")
        return False

    with open(APP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérifier si les routes sont déjà présentes
    has_import_pages = "AdminPagesList" in content
    has_import_builder = "PageBuilder" in content
    has_route_pages = 'path="/admin/pages"' in content
    has_route_builder = 'path="/admin/pages/:pageId/builder"' in content

    if has_import_pages and has_import_builder and has_route_pages and has_route_builder:
        print("  [SKIP] Routes déjà présentes")
        return True

    shutil.copy2(APP_PATH, APP_PATH + ".bak")

    # 1. Ajouter les imports
    if not has_import_pages or not has_import_builder:
        imports = (
            'import AdminPagesList from "./pages/admin/AdminPagesList";\n'
            'import PageBuilder from "./pages/admin/PageBuilder";\n'
        )
        # Insérer après le premier import de page existant
        marker = 'import Home from "./pages/Home'
        if marker in content:
            content = content.replace(marker, imports + marker, 1)
        else:
            # Sinon, après la première ligne d'import
            first_import = re.search(r'^import\s+', content, re.MULTILINE)
            if first_import:
                content = content[:first_import.start()] + imports + content[first_import.start():]
        print("  [OK] Imports ajoutés")

    # 2. Ajouter les routes
    if not has_route_pages or not has_route_builder:
        routes = '''                    {/* === Admin : Page Builder === */}
                    <Route path="/admin/pages" element={<AdminPagesList />} />
                    <Route path="/admin/pages/:pageId/builder" element={<PageBuilder />} />

'''
        # Chercher la route NotFound (le marker le plus fiable)
        patterns = [
            r'(\s*<Route path="\*" element=\{<NotFound\s*/>\}\s*/>)',
            r'(\s*<Route path="\*" element=\{<NotFound\s*></NotFound>\}\s*/>)',
        ]
        replaced = False
        for pattern in patterns:
            m = re.search(pattern, content)
            if m:
                content = content[:m.start()] + "\n" + routes + content[m.start():]
                replaced = True
                break

        if replaced:
            print("  [OK] Routes ajoutées avant NotFound")
        else:
            print("  [ATTENTION] Route NotFound introuvable. Ajout en fin de <Routes>.")
            # Fallback : insérer avant la dernière balise </Routes>
            last_routes = content.rfind("</Routes>")
            if last_routes != -1:
                content = content[:last_routes] + routes + content[last_routes:]
                print("  [OK] Routes ajoutées en fin de <Routes>")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] App.jsx mis à jour")
    return True


# ============================================================
#                    VÉRIFICATION
# ============================================================

def verify():
    print("\n--- Vérification ---")
    errors = []

    # PageBuilder
    if os.path.exists(PAGE_BUILDER):
        with open(PAGE_BUILDER, "r", encoding="utf-8") as f:
            content = f.read()
        if 'from "../puck/config"' in content or 'from "../utils/api"' in content:
            errors.append("PageBuilder.jsx contient encore des imports cassés")

    # App.jsx
    if os.path.exists(APP_PATH):
        with open(APP_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if 'path="/admin/pages"' not in content:
            errors.append('App.jsx ne contient pas la route "/admin/pages"')
        if 'path="/admin/pages/:pageId/builder"' not in content:
            errors.append('App.jsx ne contient pas la route "/admin/pages/:pageId/builder"')

    if errors:
        print("  ⚠️  Problèmes restants :")
        for e in errors:
            print(f"    - {e}")
        return False
    print("  ✅ Tous les problèmes sont corrigés")
    return True


def main():
    print("=" * 60)
    print("  CORRECTION AUDIT FRONTEND")
    print("=" * 60)
    print()

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    fix_page_builder_imports()
    fix_app_routes()
    ok = verify()

    print()
    print("=" * 60)
    if ok:
        print("  ✅ CORRECTIONS APPLIQUÉES")
        print("=" * 60)
        print("\nÉtapes suivantes :")
        print("  1. Relancer l'audit : python frontend_audit.py")
        print("  2. Redémarrer Vite : npm run dev")
        print("  3. Tester : http://localhost:5173/admin/pages")
    else:
        print("  ⚠️  Corrections partielles")
        print("=" * 60)
        print("\nVérifiez les backups :")
        print("  - src/pages/admin/PageBuilder.jsx.bak")
        print("  - src/App.jsx.bak")


if __name__ == "__main__":
    main()