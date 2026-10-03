"""
Répare les fichiers cassés par le premier script :
insère le guillemet ouvrant manquant avant /api/...

Usage : python repair_broken_urls.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")

# Motifs cassés à réparer :
# Exemple : client.get(/api/v1/...")  → client.get("/api/v1/...")
# Exemple : fetch(/api/v1/...")       → fetch("/api/v1/...")
BROKEN_PATTERNS = [
    # .get(/api/...")     → .get("/api/...")
    (re.compile(r'(\.(?:get|post|put|patch|delete|fetch|request)\(\s*)(/api/[^\s"\'\)]*")'), r'\1"\2'),
    # axios.get(/api/...") → axios.get("/api/...")
    (re.compile(r'(\baxios\.\w+\(\s*)(/api/[^\s"\'\)]*")'), r'\1"\2'),
]


def should_skip(path):
    parts = path.replace("\\", "/").split("/")
    return any(p in ("node_modules", "dist", ".vite", "build") for p in parts)


def repair_content(content):
    """Applique les regex de réparation."""
    modified = False
    for pattern, replacement in BROKEN_PATTERNS:
        new_content, count = pattern.subn(replacement, content)
        if count > 0:
            modified = True
            content = new_content
    return content, modified


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    fixed, modified = repair_content(original)

    if not modified:
        return False

    # Backup de sécurité (une fois)
    bak = path + ".pre-repair.bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

    with open(path, "w", encoding="utf-8") as f:
        f.write(fixed)
    return True


def scan_for_broken():
    """Cherche tous les motifs cassés restants."""
    print("\n--- Scan des fichiers cassés restants ---")
    found = False
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for pattern, _ in BROKEN_PATTERNS:
                for match in pattern.finditer(content):
                    line_no = content[:match.start()].count("\n") + 1
                    print(f"  [CASSÉ] {os.path.relpath(path, BASE_DIR)}:{line_no}")
                    print(f"          {match.group(0)[:80]}")
                    found = True
    if not found:
        print("  ✅ Aucun fichier cassé détecté.")


def main():
    print("=" * 60)
    print("  RÉPARATION DES URLs CASSÉES")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    # 1. Réparer
    print("\n[1/2] Réparation des fichiers cassés...")
    repaired = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            try:
                if process_file(path):
                    rel = os.path.relpath(path, BASE_DIR)
                    print(f"  [RÉPARÉ] {rel}")
                    repaired.append(rel)
            except Exception as e:
                print(f"  [ERREUR] {path} : {e}")

    if not repaired:
        print("  Aucun fichier à réparer.")

    # 2. Scanner à nouveau
    print("\n[2/2] Vérification finale...")
    scan_for_broken()

    print()
    print("=" * 60)
    print(f"  ✅ {len(repaired)} fichier(s) réparé(s)")
    print("=" * 60)
    print("\nProchaine étape :")
    print("  1. Videz le cache Vite :")
    print("     Remove-Item -Recurse -Force node_modules\\.vite")
    print("  2. Relancez : npm run dev")
    print("  3. Rechargez : Ctrl + Shift + R")


if __name__ == "__main__":
    main()