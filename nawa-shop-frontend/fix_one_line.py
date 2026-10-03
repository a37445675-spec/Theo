"""
Retire la ligne 'ProductGrid, BlogList,' qui fait doublon dans config.jsx.
Trouve la ligne contenant exactement ces 2 noms consécutifs et la supprime.

Usage : python fix_one_line.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")

# Ligne à supprimer (celle du doublon)
TARGET_PATTERN = re.compile(r'^\s*ProductGrid,\s*BlogList,\s*$', re.MULTILINE)


def main():
    print("=" * 60)
    print("  RETRAIT CHIRURGICAL DU DOUBLON")
    print("=" * 60)

    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] {CONFIG_PATH} introuvable")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Compter les occurrences
    matches = list(TARGET_PATTERN.finditer(content))

    if not matches:
        print("\n  Aucune ligne 'ProductGrid, BlogList,' trouvée.")
        print("  Vérifiez manuellement les doublons avec :")
        print("    Select-String -Path 'src\\puck\\config.jsx' -Pattern 'ProductGrid' -Context 1,1")
        return

    print(f"\n  {len(matches)} ligne(s) cible trouvée(s) :")
    for m in matches:
        line_no = content[:m.start()].count("\n") + 1
        print(f"    Ligne {line_no} : {m.group(0).strip()}")

    if len(matches) < 1:
        return

    # Backup
    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-chirurgie.bak")
    print(f"\n  [BACKUP] config.jsx.before-chirurgie.bak")

    # Supprimer UNIQUEMENT la première occurrence
    # (la version importée garde son ProductGrid dans les imports, on retire juste la déclaration locale)
    first = matches[0]
    new_content = content[:first.start()] + content[first.end():]

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n  [OK] 1 ligne supprimée")
    print(f"\n  Total caractères avant : {len(content)}")
    print(f"  Total caractères après : {len(new_content)}")

    # Vérifier qu'il reste exactement 1 occurrence (l'import)
    remaining = TARGET_PATTERN.findall(new_content)
    print(f"\n  Occurrences restantes de 'ProductGrid, BlogList,' : {len(remaining)}")

    # Vérifier l'équilibre des accolades
    opens = new_content.count("{") - new_content.count("}")
    parens = new_content.count("(") - new_content.count(")")
    brackets = new_content.count("[") - new_content.count("]")

    print(f"\n--- Vérification syntaxique ---")
    print(f"  Accolades      : {'OK' if opens == 0 else f'DÉSÉQUILIBRE ({opens:+d})'}")
    print(f"  Parenthèses    : {'OK' if parens == 0 else f'DÉSÉQUILIBRE ({parens:+d})'}")
    print(f"  Crochets       : {'OK' if brackets == 0 else f'DÉSÉQUILIBRE ({brackets:+d})'}")

    if opens == 0 and parens == 0 and brackets == 0:
        print("\n  ✅ Structure équilibrée")
        print("\n  Redémarrer Vite :")
        print("    Remove-Item -Recurse -Force node_modules\\.vite")
        print("    npm run dev")
    else:
        print("\n  ⚠️  Structure cassée")
        print("  Restaurez depuis le backup :")
        print("    Copy-Item 'src\\puck\\config.jsx.before-chirurgie.bak' 'src\\puck\\config.jsx' -Force")


if __name__ == "__main__":
    main()