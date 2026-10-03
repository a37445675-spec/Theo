"""
Exclut les vues APIView sans serializer du schéma OpenAPI.
Corrige le 500 sur /api/schema/ et /api/docs/.

Usage : python fix_schema_views.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# (chemin, liste de classes à exclure)
TARGETS = [
    ("apps/cart/views.py", ["CartView", "CartAddLineView", "CartLineDetailView"]),
    ("apps/bookings/views.py", ["BookSlotView"]),
    ("apps/accounts/views.py", ["MeView"]),
]


def ensure_import(content):
    """Ajoute l'import @extend_schema s'il n'existe pas."""
    if "from drf_spectacular.utils import extend_schema" in content:
        return content, False
    if "extend_schema" in content:
        return content, False

    # Insérer après la première ligne d'import
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            lines.insert(i, "from drf_spectacular.utils import extend_schema")
            return "\n".join(lines), True
    # Aucun import trouvé, insérer en haut
    return "from drf_spectacular.utils import extend_schema\n\n" + content, True


def patch_class(content, class_name):
    """Ajoute @extend_schema(exclude=True) avant la définition de la classe."""
    # Si déjà patché, ne rien faire
    pattern_check = re.compile(
        rf'@extend_schema\([^)]*exclude\s*=\s*True[^)]*\)\s*\n\s*class\s+{class_name}\b'
    )
    if pattern_check.search(content):
        return content, False

    # Trouver la définition de la classe
    class_pattern = re.compile(rf'^(\s*)class\s+{class_name}\b', re.MULTILINE)
    match = class_pattern.search(content)

    if not match:
        return content, False

    indent = match.group(1)
    insert_pos = match.start()
    decorator = f"{indent}@extend_schema(exclude=True)\n"

    new_content = content[:insert_pos] + decorator + content[insert_pos:]
    return new_content, True


def main():
    print("=" * 60)
    print("  CORRECTION DU SCHÉMA OPENAPI")
    print("=" * 60)

    total_patched = 0

    for rel_path, classes in TARGETS:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"  [SKIP] {rel_path} (fichier introuvable)")
            continue

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # 1. Ajouter l'import
        content, import_added = ensure_import(content)

        # 2. Patcher chaque classe
        classes_patched = []
        for cls in classes:
            content, patched = patch_class(content, cls)
            if patched:
                classes_patched.append(cls)

        if content == original and not import_added and not classes_patched:
            print(f"  [SKIP] {rel_path} (déjà patché)")
            continue

        # Backup
        shutil.copy2(full_path, full_path + ".bak")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        patched_info = f" (import: {'oui' if import_added else 'non'}"
        if classes_patched:
            patched_info += f", classes: {', '.join(classes_patched)}"
        patched_info += ")"

        print(f"  [OK] {rel_path}{patched_info}")
        total_patched += 1

    print()
    print("=" * 60)
    if total_patched:
        print(f"  ✅ {total_patched} fichier(s) patché(s)")
    else:
        print("  Aucune modification nécessaire.")
    print("=" * 60)
    print()
    print("Vérifiez ensuite :")
    print("  python manage.py spectacular --file schema.yaml 2>&1 | Select-Object -Last 10")


if __name__ == "__main__":
    main()