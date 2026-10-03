"""
Corrige l'ordre des routes CMS pour que widget_urls prime sur cms.urls.

Usage : python fix_urls_order.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_urls():
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def main():
    urls_path = find_urls()
    if not urls_path:
        print("  [ERREUR] urls.py introuvable")
        return

    print(f"  Fichier cible : {os.path.relpath(urls_path, BASE_DIR)}")

    with open(urls_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Localiser les deux lignes
    widget_line_pattern = re.compile(
        r'\s*path\("api/v1/cms/",\s*include\("apps\.cms\.widget_urls"\)\),\s*\n'
    )
    cms_line_pattern = re.compile(
        r'\s*path\("api/v1/cms/",\s*include\("apps\.cms\.urls"\)\),\s*\n'
    )

    widget_match = widget_line_pattern.search(content)
    cms_match = cms_line_pattern.search(content)

    if not widget_match or not cms_match:
        print("  [ATTENTION] Une des deux routes est absente.")
        print("  Vérifiez manuellement config/urls.py")
        return

    # Si widget_urls est déjà AVANT cms.urls → rien à faire
    if widget_match.start() < cms_match.start():
        print("  [SKIP] Ordre déjà correct")
        return

    shutil.copy2(urls_path, urls_path + ".bak")
    print(f"  [BACKUP] {os.path.relpath(urls_path, BASE_DIR)}.bak")

    # Extraire les lignes
    widget_line = widget_match.group(0)
    cms_line = cms_match.group(0)

    # Retirer les deux lignes
    content = content.replace(widget_line, "")
    content = content.replace(cms_line, "")

    # Trouver l'endroit où insérer (avant la première route /api/v1/cms/)
    # On insère widget puis cms à la place de l'ancienne ligne cms
    insertion_point = cms_match.start()
    # Recalculer car on a retiré du contenu
    # Chercher un repère stable : la ligne "path(\"api/v1/cms/\", include(\"apps.cms.urls\"))" originale n'existe plus
    # On va plutôt insérer AVANT la première ligne "/api/v1/cms/" qui reste

    # Chercher la première occurrence restante de "api/v1/cms/"
    idx = content.find('path("api/v1/cms/",')
    if idx == -1:
        print("  [ATTENTION] Impossible de trouver le point d'insertion.")
        return

    insertion = (
        '    # === Widget Builder (doit primer sur cms.urls) ===\n'
        + widget_line.rstrip() + "\n"
        + '    # === CMS général ===\n'
        + cms_line.rstrip() + "\n"
    )

    content = content[:idx] + insertion + content[idx:]

    with open(urls_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("  [OK] Routes réordonnées : widget_urls AVANT cms.urls")


if __name__ == "__main__":
    main()