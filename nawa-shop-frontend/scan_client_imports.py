"""
Scanne tous les imports depuis ./client pour savoir exactement
ce que client.js doit exporter.

Usage : python scan_client_imports.py
"""
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def main():
    print("=" * 60)
    print("  SCAN DES IMPORTS DEPUIS client.js")
    print("=" * 60)
    print()

    imports = {}  # {nom_importé: [fichiers]}
    patterns = [
        re.compile(r'import\s*\{([^}]+)\}\s*from\s*["\'][^"\']*client(?:\.js)?["\']'),
        re.compile(r'import\s*\{([^}]+)\}\s*from\s*["\'][^"\']*\/client(?:\.js)?["\']'),
    ]

    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for f in files:
            if not f.endswith(EXTENSIONS) or f.endswith(".bak"):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, BASE_DIR)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except Exception:
                continue

            for pat in patterns:
                for m in pat.finditer(content):
                    names = [n.strip() for n in m.group(1).split(",")]
                    for name in names:
                        name = name.split(" as ")[0].strip()
                        if name and re.match(r'^\w+$', name):
                            imports.setdefault(name, []).append(rel)

    if not imports:
        print("  Aucun import depuis client.js trouvé.")
        return

    print(f"  {len(imports)} symboles importés depuis client.js :\n")
    for name in sorted(imports.keys()):
        files = imports[name]
        print(f"  • {name}")
        for f in files[:3]:
            print(f"      ← {f}")
        if len(files) > 3:
            print(f"      ... et {len(files)-3} autres")

    print()
    print("=" * 60)
    print("  Recopiez cette liste pour construire client.js")
    print("=" * 60)


if __name__ == "__main__":
    main()