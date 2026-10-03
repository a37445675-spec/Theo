"""
Corrige CmsContext.jsx : /api/v1/cms/design-system/ → /api/v1/design-system/active/

Usage : python fix_cms_context.py
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTEXT_PATH = os.path.join(BASE_DIR, "src", "context", "CmsContext.jsx")


def main():
    print("=" * 60)
    print("  CORRECTION CmsContext.jsx")
    print("=" * 60)

    if not os.path.exists(CONTEXT_PATH):
        print(f"  [ERREUR] {CONTEXT_PATH} introuvable")
        return

    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérifier l'URL actuelle
    if "/api/v1/cms/design-system/" not in content and "/api/v1/cms/design-system/active/" not in content:
        print("  [INFO] Aucune URL à corriger dans CmsContext.jsx")
        print(f"  [INFO] Contenu des URLs détectées :")
        for line in content.split("\n"):
            if "design-system" in line or "/api/" in line:
                print(f"        {line.strip()[:100]}")
        return

    original = content

    # Corriger les URLs
    content = content.replace(
        "/api/v1/cms/design-system/active/",
        "/api/v1/design-system/active/"
    )
    content = content.replace(
        "/api/v1/cms/design-system/",
        "/api/v1/design-system/active/"
    )

    if content == original:
        print("  [SKIP] Aucun changement effectué")
        return

    # Backup
    with open(CONTEXT_PATH + ".bak", "w", encoding="utf-8") as f:
        f.write(original)

    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("  [OK] CmsContext.jsx corrigé")
    print("  [OK] Backup créé : CmsContext.jsx.bak")
    print()

    # Afficher les nouvelles URLs
    print("  URLs après correction :")
    for line in content.split("\n"):
        if "design-system" in line:
            print(f"    {line.strip()[:100]}")

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print()
    print("Redémarrez le frontend :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()