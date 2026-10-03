"""
Corrige le config.jsx pour ajouter les 17 widgets P10 manquants.
Analyse la structure réelle et insère intelligemment.

Usage : python fix_p10_config.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")


# Imports P10 à ajouter
IMPORTS_P10 = '''
/* === PHASE 10 WIDGETS (fix) === */
import {
  PostTitle, PostContent, PostExcerpt, PostInfo,
  PostNavigation, PostComments, AuthorBox,
} from "./widgets/postWidgets";
import {
  ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,
  Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,
} from "./widgets/archiveWidgets";
/* === FIN PHASE 10 === */
'''

# Composants à ajouter
COMPONENTS_P10 = """    // === Phase 10 : Post dynamique ===
    PostTitle, PostContent, PostExcerpt, PostInfo,
    PostNavigation, PostComments, AuthorBox,
    // === Phase 10 : Archive & Site ===
    ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,
    Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,
"""

# Catégories à ajouter
CATEGORIES_P10 = """    postDynamic: { title: "Article (dynamique)", components: [
      "PostTitle", "PostContent", "PostExcerpt", "PostInfo",
      "PostNavigation", "PostComments", "AuthorBox",
    ]},
    archiveDynamic: { title: "Archive & Liste", components: [
      "ArchiveTitle", "ArchivePosts", "Breadcrumbs",
      "LoopGrid", "LoopCarousel", "Taxonomy", "PostPortfolio",
    ]},
    siteIdentity: { title: "Identité du site", components: [
      "SiteLogo", "SiteTitle", "SitelinkSearch",
    ]},
"""


def main():
    print("=" * 60)
    print("  CORRECTION config.jsx — Ajout des 17 widgets P10")
    print("=" * 60)

    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable : {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Étape 1 : Vérifier si les imports P10 sont déjà là
    if "from \"./widgets/postWidgets\"" in content:
        print("  [SKIP] Imports P10 déjà présents")
    else:
        print("  [1/3] Ajout des imports P10...")
        # Insérer après le dernier import (avant la première const)
        const_match = re.search(r'^const\s+\w+', content, re.MULTILINE)
        if const_match:
            content = (
                content[:const_match.start()]
                + IMPORTS_P10 + "\n"
                + content[const_match.start():]
            )
            print("       Imports insérés avant la première const")
        else:
            content = IMPORTS_P10 + "\n" + content
            print("       Imports insérés en haut du fichier")

    # Étape 2 : Ajouter les composants dans puckConfig.components
    print("  [2/3] Ajout des composants dans puckConfig.components...")
    if "PostTitle," in content and "puckConfig" in content:
        # Vérifier que c'est bien dans components et pas juste dans l'import
        comp_match = re.search(r'components:\s*\{', content)
        if comp_match:
            # Chercher la fermeture de components
            start = comp_match.end()
            # Compter les accolades pour trouver la fin
            depth = 1
            i = start
            while i < len(content) and depth > 0:
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                i += 1
            end = i - 1  # position du }

            # Insérer avant la fermeture
            before = content[:end]
            after = content[end:]
            content = before.rstrip() + "\n" + COMPONENTS_P10 + "  " + after
            print("       Composants ajoutés dans puckConfig.components")
    else:
        print("       [ATTENTION] Structure components introuvable")

    # Étape 3 : Ajouter les catégories
    print("  [3/3] Ajout des catégories...")
    if '"Article (dynamique)"' not in content:
        cat_match = re.search(r'categories:\s*\{', content)
        if cat_match:
            start = cat_match.end()
            depth = 1
            i = start
            while i < len(content) and depth > 0:
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                i += 1
            end = i - 1

            before = content[:end]
            after = content[end:]
            content = before.rstrip() + "\n" + CATEGORIES_P10 + "  " + after
            print("       Catégories ajoutées dans puckConfig.categories")
    else:
        print("       [SKIP] Catégories déjà présentes")

    # Backup + sauvegarde
    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-p10-fix.bak")
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n" + "=" * 60)
    print("  ✅ config.jsx corrigé")
    print("=" * 60)
    print("\nBackup : config.jsx.before-p10-fix.bak")
    print("\nVérifiez ensuite :")
    print("  Select-String -Path 'src\\puck\\config.jsx' -Pattern 'postWidgets|PostTitle'")
    print("\nPuis relancez :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()