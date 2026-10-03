"""
Correction des URLs API dans tout le frontend.
Corrige les 404 en alignant les appels frontend sur les routes réelles du backend.

Usage : python fix_api_urls.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# ============================================================
#  Corrections spécifiques (ordre : plus spécifique d'abord)
# ============================================================

FIXES = [
    # 1. CMS : page-templates → templates (route réelle Django)
    ("/api/v1/cms/page-templates/", "/api/v1/cms/templates/"),
    ("/api/page-templates/", "/api/v1/cms/templates/"),
    # 2. Design System : ne pas passer par /cms/
    ("/api/v1/cms/design-system/active/", "/api/v1/design-system/active/"),
    ("/api/v1/cms/design-system/", "/api/v1/design-system/active/"),
    # 3. Toutes les routes sans /v1/ → ajouter /v1/
    ("/api/blog/", "/api/v1/blog/"),
    ("/api/catalog/", "/api/v1/catalog/"),
    ("/api/cart/", "/api/v1/cart/"),
    ("/api/checkout/", "/api/v1/checkout/"),
    ("/api/orders/", "/api/v1/orders/"),
    ("/api/auth/", "/api/v1/auth/"),
    ("/api/cms/", "/api/v1/cms/"),
    ("/api/design-system/", "/api/v1/design-system/"),
    ("/api/navigation/", "/api/v1/navigation/"),
    ("/api/seo/", "/api/v1/seo/"),
    ("/api/translations/", "/api/v1/translations/"),
    ("/api/feature-flags/", "/api/v1/feature-flags/"),
    ("/api/announcements/", "/api/v1/announcements/"),
    ("/api/media-library/", "/api/v1/media-library/"),
    ("/api/forms/", "/api/v1/forms/"),
    ("/api/redirects/", "/api/v1/redirects/"),
    ("/api/third-party-scripts/", "/api/v1/third-party-scripts/"),
    ("/api/email-templates/", "/api/v1/email-templates/"),
]


EXTENSIONS = (".js", ".jsx", ".ts", ".tsx")


def should_skip(path):
    parts = path.replace("\\", "/").split("/")
    return any(p in ("node_modules", "dist", ".vite", "build") for p in parts)


def fix_content(content):
    """Applique les corrections dans l'ordre."""
    modified = False
    for old, new in FIXES:
        if old in content:
            content = content.replace(old, new)
            modified = True

    # Corriger les appels fetch sans slash initial : "api/..." → "/api/v1/..."
    def add_v1_no_slash(match):
        nonlocal modified
        rest = match.group(2)
        if rest.startswith("v1/") or rest.startswith("v2/"):
            return match.group(0)
        modified = True
        return f'{match.group(1)}/api/v1/{rest}'

    content = re.sub(
        r'(["\'])(?<!/)api/(?!v\d/)([^"\']*)',
        add_v1_no_slash,
        content,
    )

    return content, modified


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    fixed, modified = fix_content(original)

    if not modified:
        return False

    shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(fixed)
    return True


def main():
    print("=" * 60)
    print("  CORRECTION DES URLs API — NAWA")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    fixed_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for filename in files:
            if not filename.endswith(EXTENSIONS) or filename.endswith(".bak"):
                continue
            path = os.path.join(root, filename)
            rel = os.path.relpath(path, BASE_DIR)
            try:
                if process_file(path):
                    print(f"  [FIX] {rel}")
                    fixed_files.append(rel)
            except Exception as e:
                print(f"  [ERREUR] {rel} : {e}")

    print()
    print("=" * 60)
    if fixed_files:
        print(f"  ✅ {len(fixed_files)} fichier(s) corrigé(s)")
        print("=" * 60)
        print("\nVérifiez ensuite :")
        print("  Select-String -Path 'src\\**\\*.jsx' -Pattern '/api/(?!v1)'")
    else:
        print("  Aucun fichier à corriger.")
        print("=" * 60)


if __name__ == "__main__":
    main()