"""
Corrige toutes les références à /api/v1/cms/page-templates/ → /api/v1/cms/templates/

Usage : python fix_page_templates_url.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

REPLACEMENTS = [
    ("/api/v1/cms/page-templates/", "/api/v1/cms/templates/"),
    ("/api/cms/page-templates/", "/api/v1/cms/templates/"),
    ("/api/v1/cms/page-templates", "/api/v1/cms/templates"),
    ("/api/cms/page-templates", "/api/v1/cms/templates"),
]

EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def main():
    print("=" * 60)
    print("  CORRECTION page-templates → templates")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    fixed = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            for old, new in REPLACEMENTS:
                content = content.replace(old, new)

            if content != original:
                shutil.copy2(path, path + ".bak")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                rel = os.path.relpath(path, BASE_DIR)
                print(f"  [FIX] {rel}")
                fixed.append(rel)

    print()
    if fixed:
        print(f"  ✅ {len(fixed)} fichier(s) corrigé(s)")
    else:
        print("  Aucun fichier à corriger.")

    # Vérification
    print("\n--- Vérification finale ---")
    remaining = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                if "page-templates" in f.read():
                    remaining.append(os.path.relpath(path, BASE_DIR))

    if remaining:
        print(f"  ⚠️  Il reste des références :")
        for r in remaining:
            print(f"    - {r}")
    else:
        print("  ✅ Plus aucune référence à page-templates")

    print()
    print("=" * 60)
    print("  Ensuite :")
    print("    1. Relancer : npm run dev")
    print("    2. Tester  : http://localhost:5173/admin/pages")


if __name__ == "__main__":
    main()