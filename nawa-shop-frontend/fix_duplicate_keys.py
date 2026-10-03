"""
Retire les doublons dans config.jsx (ProductGrid, BlogList, etc.).
Garde la version importée (Phase 11) et supprime la version locale (Phase 7).

Usage : python fix_duplicate_keys.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")


def find_duplicates_in_components(content):
    """Trouve les clés en double dans puckConfig.components."""
    m = re.search(r'components:\s*\{', content)
    if not m:
        return []

    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1

    block = content[start:i-1]
    block_start = start

    # Extraire tous les identifiants
    keys = []
    for line in block.split("\n"):
        line_clean = re.sub(r'//.*$', '', line)
        line_clean = re.sub(r'/\*.*?\*/', '', line_clean, flags=re.DOTALL)
        for part in line_clean.split(","):
            part = part.strip()
            if re.match(r'^\w+$', part):
                keys.append(part)

    # Trouver les doublons
    seen = set()
    duplicates = set()
    for k in keys:
        if k in seen:
            duplicates.add(k)
        seen.add(k)

    return list(duplicates), block_start, i - 1


def remove_duplicate_occurrence(content, key, block_start, block_end):
    """
    Retire la 2ème occurrence (ou plus) d'un identifiant dans le bloc components.
    On garde la première (qui est l'import Phase 11).
    """
    block = content[block_start:block_end]

    # Trouver toutes les occurrences
    pattern = re.compile(rf'(?:^|,|\n)\s*{re.escape(key)}\s*(?:,|\n|$)')
    matches = list(pattern.finditer(block))

    if len(matches) <= 1:
        return content, 0

    # Supprimer toutes sauf la première (en partant de la fin pour ne pas casser les index)
    removed = 0
    for match in reversed(matches[1:]):
        block = block[:match.start()] + block[match.end():]
        removed += 1

    new_content = content[:block_start] + block + content[block_end:]
    return new_content, removed


def main():
    print("=" * 60)
    print("  SUPPRESSION DES DOUBLONS DANS config.jsx")
    print("=" * 60)

    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] {CONFIG_PATH} introuvable")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    duplicates, block_start, block_end = find_duplicates_in_components(content)

    if not duplicates:
        print("\n  ✅ Aucun doublon détecté")
        return

    print(f"\n  Doublons détectés : {duplicates}")

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-dedup.bak")
    print(f"  [BACKUP] config.jsx.before-dedup.bak\n")

    total_removed = 0
    for key in duplicates:
        # Recalculer à chaque fois car le contenu change
        _, bs, be = find_duplicates_in_components(content)
        content, removed = remove_duplicate_occurrence(content, key, bs, be)
        if removed:
            print(f"  [OK] {key} : {removed} occurrence(s) retirée(s)")
            total_removed += removed

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n  Total : {total_removed} occurrence(s) retirée(s)")

    # Vérification finale
    final_dupes, _, _ = find_duplicates_in_components(content)
    if final_dupes:
        print(f"\n  ⚠️  Doublons restants : {final_dupes}")
    else:
        print("\n  ✅ Plus aucun doublon")

    print()
    print("=" * 60)
    print("  Redémarrer Vite :")
    print("    Remove-Item -Recurse -Force node_modules\\.vite")
    print("    npm run dev")


if __name__ == "__main__":
    main()