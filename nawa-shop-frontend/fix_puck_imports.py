"""
Corrige les imports @measured/puck → @puckeditor/core dans tous les fichiers.
Et vérifie que PublicPageRenderer utilise aussi le bon package.

Usage : python fix_puck_imports.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

REPLACEMENTS = [
    ('from "@measured/puck"', 'from "@puckeditor/core"'),
    ('from "@measured/puck/puck.css"', 'from "@puckeditor/core/puck.css"'),
    ('import "@measured/puck/puck.css"', 'import "@puckeditor/core/puck.css"'),
    ('@measured/puck', '@puckeditor/core'),
]

EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def main():
    print("=" * 60)
    print("  CORRECTION @measured/puck → @puckeditor/core")
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

    # Vérification finale
    print("\n--- Vérification ---")
    remaining = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                if "@measured/puck" in f.read():
                    remaining.append(os.path.relpath(path, BASE_DIR))

    if remaining:
        print(f"  ⚠️  Il reste des références :")
        for r in remaining:
            print(f"    - {r}")
    else:
        print("  ✅ Plus aucune référence à @measured/puck")

    print()
    print("=" * 60)
    print("  Ensuite :")
    print("    1. Vérifier package.json : @puckeditor/core doit être installé")
    print("    2. Vider le cache : Remove-Item -Recurse -Force node_modules\\.vite")
    print("    3. Relancer : npm run dev")


if __name__ == "__main__":
    main()