"""
Corrige les doublons dans config.jsx :
- ProductGrid (Phase 7 local vs Phase 11 importé)
- BlogList (potentiellement idem)
- Tout autre widget déclaré localement ET importé

Usage : python fix_config_duplicates.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")


def find_local_declarations(content):
    """Trouve toutes les déclarations 'const X = {...}' locales."""
    declarations = []
    pattern = re.compile(r'^const\s+(\w+)\s*=\s*\{', re.MULTILINE)
    for m in pattern.finditer(content):
        declarations.append({
            "name": m.group(1),
            "start": m.start(),
        })
    return declarations


def find_imported_names(content):
    """Trouve les noms importés depuis ./widgets/."""
    imported = set()
    pattern = re.compile(r'import\s*\{([^}]+)\}\s*from\s*["\']\./widgets/')
    for m in pattern.finditer(content):
        for name in m.group(1).split(","):
            name = name.strip()
            if name and re.match(r'^\w+$', name):
                imported.add(name)
    return imported


def find_block_end(content, start):
    """
    Trouve la fin d'un bloc JSX/objet ouvert à 'start'.
    Retourne l'index de fin (juste après le '};' ou '},').
    """
    # Chercher la fin du const : "};" suivi d'un retour à la ligne
    # On utilise un compteur d'accolades pour trouver la fin
    depth = 0
    i = start
    started = False
    while i < len(content):
        c = content[i]
        if c == "{":
            depth += 1
            started = True
        elif c == "}":
            depth -= 1
            if started and depth == 0:
                # Trouver le ; ou , suivant
                j = i + 1
                while j < len(content) and content[j] in " \t":
                    j += 1
                if j < len(content) and content[j] in ";,":
                    return j + 1
                return i + 1
        i += 1
    return -1


def remove_local_duplicate(content, name):
    """Supprime la déclaration locale 'const NAME = {...};'."""
    pattern = re.compile(rf'^const\s+{re.escape(name)}\s*=\s*\{{', re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return content, False

    start = match.start()
    end = find_block_end(content, match.end() - 1)
    if end == -1:
        return content, False

    # Inclure la ligne suivante s'il y a un \n
    while end < len(content) and content[end] in "\n\r":
        end += 1

    new_content = content[:start] + content[end:]
    return new_content, True


def main():
    print("=" * 60)
    print("  CORRECTION DES DOUBLONS DANS config.jsx")
    print("=" * 60)
    print()

    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] {CONFIG_PATH} introuvable")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"  Taille avant : {len(content)} caractères")

    # 1. Trouver les déclarations locales
    locals_found = find_local_declarations(content)
    local_names = {d["name"] for d in locals_found}
    print(f"\n  Déclarations locales : {sorted(local_names)}")

    # 2. Trouver les imports
    imported = find_imported_names(content)
    print(f"  Imports trouvés     : {len(imported)} widgets")

    # 3. Trouver les conflits (déclarés localement ET importés)
    conflicts = local_names & imported
    print(f"\n  Conflits détectés   : {sorted(conflicts)}")

    if not conflicts:
        print("\n  ✅ Aucun conflit à corriger.")
        return

    # 4. Backup
    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-dedup.bak")
    print(f"\n  [BACKUP] config.jsx.before-dedup.bak")

    # 5. Supprimer les déclarations locales en conflit
    for name in conflicts:
        content, removed = remove_local_duplicate(content, name)
        if removed:
            print(f"  [OK] Déclaration locale de '{name}' supprimée")
        else:
            print(f"  [ATTENTION] Impossible de supprimer '{name}'")

    # 6. Sauvegarder
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n  Taille après : {len(content)} caractères")

    # 7. Vérifier qu'il ne reste plus de doublons
    print("\n--- Vérification ---")
    remaining_locals = {d["name"] for d in find_local_declarations(content)}
    remaining_conflicts = remaining_locals & imported
    if remaining_conflicts:
        print(f"  ⚠️  Conflits restants : {remaining_conflicts}")
    else:
        print("  ✅ Plus aucun conflit")

    print()
    print("=" * 60)
    print("  ✅ CORRECTION APPLIQUÉE")
    print("=" * 60)
    print("\nÉtapes suivantes :")
    print("  1. Vider le cache : Remove-Item -Recurse -Force node_modules\\.vite")
    print("  2. Relancer      : npm run dev")


if __name__ == "__main__":
    main()