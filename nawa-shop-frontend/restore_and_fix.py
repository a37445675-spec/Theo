"""
Restaure les backups et réapplique une correction sûre des URLs API.

Usage : python restore_and_fix.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def should_skip(path):
    parts = path.replace("\\", "/").split("/")
    return any(p in ("node_modules", "dist", ".vite", "build") for p in parts)


def restore_backups():
    """Restaure tous les .bak en écrasant l'original."""
    print("[1/3] Restauration des backups...")
    restored = 0
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(".bak"):
                continue
            bak_path = os.path.join(root, filename)
            original_path = bak_path[:-4]  # retire ".bak"
            if os.path.exists(original_path):
                shutil.copy2(bak_path, original_path)
                print(f"  [RESTORE] {os.path.relpath(original_path, BASE_DIR)}")
                restored += 1
    print(f"  → {restored} fichier(s) restauré(s)\n")
    return restored


def fix_content(content):
    """
    Correction SÛRE :
    - Utilise un lookbehind (ne consomme pas le guillemet)
    - Ne matche que les URLs précédées d'un guillemet ou backtick
    - Ignore celles déjà en /v1/
    """
    # Correction spécifique : page-templates → templates
    content = content.replace("/api/v1/cms/page-templates/", "/api/v1/cms/templates/")
    content = content.replace("/api/cms/page-templates/", "/api/v1/cms/templates/")

    # Correction spécifique : cms/design-system → design-system
    content = content.replace("/api/v1/cms/design-system/active/", "/api/v1/design-system/active/")
    content = content.replace("/api/v1/cms/design-system/", "/api/v1/design-system/active/")

    # Correction générique SÛRE : /api/xxx → /api/v1/xxx
    # Le (?<=["'`]) regarde en arrière SANS consommer le guillemet
    # Le (?!v\d/) empêche de doubler la version
    original = content
    content = re.sub(
        r'(?<=["\'`])/api/(?!v\d/)',
        '/api/v1/',
        content,
    )

    return content, content != original


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    fixed, modified = fix_content(original)

    if not modified:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(fixed)
    return True


def apply_fixes():
    print("[2/3] Application des corrections sûres...")
    fixed_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            try:
                if process_file(path):
                    print(f"  [FIX] {os.path.relpath(path, BASE_DIR)}")
                    fixed_files.append(path)
            except Exception as e:
                print(f"  [ERREUR] {path} : {e}")
    print(f"  → {len(fixed_files)} fichier(s) corrigé(s)\n")
    return fixed_files


def verify():
    """Cherche des motifs suspects : guillemets manquants autour des URLs."""
    print("[3/3] Vérification...")
    issues = []
    pattern_bad = re.compile(r'\.(get|post|put|patch|delete|fetch)\s*\(\s*api/')
    pattern_bad2 = re.compile(r'\.(get|post|put|patch|delete)\s*\(\s*/api/')

    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if pattern_bad.search(content) or pattern_bad2.search(content):
                issues.append(os.path.relpath(path, BASE_DIR))

    if issues:
        print("  ⚠️  Fichiers suspects détectés :")
        for i in issues:
            print(f"    - {i}")
        print("\n  Ouvrez-les manuellement pour vérifier la syntaxe.")
    else:
        print("  ✅ Aucun motif suspect détecté.")


def main():
    print("=" * 60)
    print("  RESTAURATION + CORRECTION SÛRE DES URLs API")
    print("=" * 60)
    print()

    restore_backups()
    apply_fixes()
    verify()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\nProchaine étape :")
    print("  1. Relancez Vite : npm run dev")
    print("  2. Rechargez le navigateur : Ctrl + Shift + R")


if __name__ == "__main__":
    main()