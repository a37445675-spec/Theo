"""
Retire 2 lignes précises qui sont des doublons dans config.jsx :
- Ligne contenant exactement : `    ProductGrid, BlogList,`
- Ligne contenant exactement : `    commerce: { title: "Boutique", components: ["ProductGrid", "BlogList"] },`

Usage : python fix_config_final.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")

# Lignes exactes à supprimer (avec indentation)
LINES_TO_REMOVE = [
    "    ProductGrid, BlogList,",
    '    commerce: { title: "Boutique", components: ["ProductGrid", "BlogList"] },',
]


def main():
    print("=" * 60)
    print("  CORRECTION FINALE DE config.jsx")
    print("=" * 60)

    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] {CONFIG_PATH} introuvable")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"\n  Lignes totales : {len(lines)}")

    # Backup
    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-final.bak")
    print(f"  [BACKUP] config.jsx.before-final.bak")

    # Trouver et marquer les lignes à supprimer
    to_remove = []
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n\r")
        for target in LINES_TO_REMOVE:
            if stripped == target:
                to_remove.append((i, target))
                print(f"  [TROUVÉ] Ligne {i + 1} : {target.strip()}")

    if not to_remove:
        print("\n  ⚠️  Aucune ligne cible trouvée.")
        print("  Le fichier a peut-être déjà été corrigé.")
        return

    # Supprimer en partant de la fin pour ne pas casser les index
    for idx, _ in sorted(to_remove, reverse=True):
        del lines[idx]

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n  [OK] {len(to_remove)} ligne(s) supprimée(s)")
    print(f"  Lignes après : {len(lines)}")

    # Vérification syntaxique
    content = "".join(lines)
    opens = content.count("{") - content.count("}")
    parens = content.count("(") - content.count(")")
    brackets = content.count("[") - content.count("]")

    print(f"\n--- Vérification syntaxique ---")
    print(f"  Accolades    : {'OK' if opens == 0 else f'DÉSÉQUILIBRE ({opens:+d})'}")
    print(f"  Parenthèses  : {'OK' if parens == 0 else f'DÉSÉQUILIBRE ({parens:+d})'}")
    print(f"  Crochets     : {'OK' if brackets == 0 else f'DÉSÉQUILIBRE ({brackets:+d})'}")

    # Vérifier qu'il reste bien ProductGrid une seule fois dans components
    product_grid_count = content.count("ProductGrid")
    print(f"\n  Occurrences de 'ProductGrid' : {product_grid_count}")

    if opens == 0 and parens == 0 and brackets == 0:
        print("\n  ✅ Structure équilibrée")
        print("\n  Étapes suivantes :")
        print("    1. Remove-Item -Recurse -Force node_modules\\.vite")
        print("    2. npm run dev")
    else:
        print("\n  ⚠️  Structure cassée — restaurez depuis le backup :")
        print("    Copy-Item 'src\\puck\\config.jsx.before-final.bak' 'src\\puck\\config.jsx' -Force")


if __name__ == "__main__":
    main()