"""
Corrige DynamicAttributeFilterBackend en ajoutant get_schema_operation_parameters().
Résout le crash de /api/schema/ et /api/docs/.

Usage : python fix_filter_backend.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Méthode à ajouter dans la classe
SCHEMA_METHOD = '''
    def get_schema_operation_parameters(self, view):
        """Permet à drf-spectacular de documenter ce filtre."""
        return [
            {
                "name": "attributes",
                "required": False,
                "in": "query",
                "description": "Filtre par attributs dynamiques (format: code=valeur)",
                "schema": {"type": "string"},
            },
        ]
'''


def find_filter_file():
    """Cherche le fichier contenant DynamicAttributeFilterBackend."""
    for root, dirs, files in os.walk(BASE_DIR):
        # Exclure venv, node_modules, .git
        dirs[:] = [d for d in dirs if d not in ("venv", ".venv", "node_modules", ".git", "__pycache__")]
        for filename in files:
            if not filename.endswith(".py"):
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "class DynamicAttributeFilterBackend" in content:
                    return path, content
            except Exception:
                continue
    return None, None


def patch_file(path, content):
    """Ajoute la méthode get_schema_operation_parameters."""
    # Si déjà présent, ne rien faire
    if "get_schema_operation_parameters" in content:
        print(f"  [SKIP] Méthode déjà présente dans {os.path.relpath(path, BASE_DIR)}")
        return False

    # Trouver la classe DynamicAttributeFilterBackend
    class_pattern = re.compile(
        r'(class DynamicAttributeFilterBackend\([^)]+\):\s*\n)',
        re.MULTILINE,
    )
    match = class_pattern.search(content)
    if not match:
        print(f"  [ERREUR] Impossible de trouver la classe dans {path}")
        return False

    # Trouver la fin de la classe (première ligne non indentée après la déclaration)
    class_start = match.end()
    lines = content[class_start:].split("\n")
    insert_at = class_start
    for line in lines:
        if line and not line.startswith((" ", "\t")) and not line.startswith("#"):
            # Fin de la classe
            break
        insert_at += len(line) + 1  # +1 pour le \n

    # Insérer la méthode à la fin de la classe
    new_content = content[:insert_at] + SCHEMA_METHOD + "\n" + content[insert_at:]

    # Backup
    shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  [OK] Méthode ajoutée dans {os.path.relpath(path, BASE_DIR)}")
    print(f"       Backup : {os.path.relpath(path, BASE_DIR)}.bak")
    return True


def main():
    print("=" * 60)
    print("  CORRECTION DU FILTRE DYNAMIQUE")
    print("=" * 60)
    print()

    print("[1/2] Recherche de DynamicAttributeFilterBackend...")
    path, content = find_filter_file()

    if not path:
        print("  [ERREUR] Classe DynamicAttributeFilterBackend introuvable.")
        print("  Vérifiez qu'elle existe bien dans votre projet.")
        return

    print(f"  Fichier trouvé : {os.path.relpath(path, BASE_DIR)}")
    print()

    print("[2/2] Ajout de get_schema_operation_parameters()...")
    patched = patch_file(path, content)

    print()
    print("=" * 60)
    if patched:
        print("  ✅ CORRECTION APPLIQUÉE")
    else:
        print("  Rien à faire.")
    print("=" * 60)
    print()
    print("Testez :")
    print("  python manage.py spectacular --file schema.yaml 2>&1 | Select-Object -Last 5")


if __name__ == "__main__":
    main()