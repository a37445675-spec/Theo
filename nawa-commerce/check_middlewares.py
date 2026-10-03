"""
Analyse tous les middlewares du projet pour détecter :
- Imports manquants (comme le 're' manquant)
- Erreurs de syntaxe
- Références à des modules non importés

Usage : python check_middlewares.py
"""
import ast
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, "apps")


# Modules Python couramment utilisés qui doivent être importés explicitement
COMMON_MODULES = [
    "re", "json", "os", "sys", "time", "datetime", "logging",
    "uuid", "hashlib", "base64", "random", "math", "collections",
    "itertools", "functools", "typing", "pathlib", "urllib",
]

# Couleurs
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def find_middleware_files():
    """Trouve tous les fichiers middleware.py ou middleware_*.py."""
    files = []
    for root, dirs, filenames in os.walk(APPS_DIR):
        dirs[:] = [d for d in dirs if d not in ("migrations", "__pycache__", "node_modules")]
        for f in filenames:
            if f == "middleware.py" or f.startswith("middleware_"):
                files.append(os.path.join(root, f))
    return files


def get_imported_names(tree):
    """Récupère tous les noms importés dans l'AST."""
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported.add(name)
    return imported


def find_module_usage(content, module_name):
    """Cherche si un module est utilisé (ex: re.match, json.dumps)."""
    pattern = rf'\b{re.escape(module_name)}\.'
    return bool(re.search(pattern, content))


def find_missing_imports(filepath, tree, content, imported_names):
    """Détecte les modules utilisés mais non importés."""
    missing = []
    for module in COMMON_MODULES:
        if module in imported_names:
            continue  # Déjà importé
        if find_module_usage(content, module):
            missing.append(module)
    return missing


def find_undefined_names(tree):
    """Détecte les noms utilisés mais non définis ni importés (approximatif)."""
    # Collecte des noms définis (fonctions, classes, variables au top-level)
    defined = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)

    # Noms builtins Python (à ignorer)
    builtins = set(dir(__builtins__)) | {
        "self", "cls", "True", "False", "None",
        "Exception", "ValueError", "TypeError", "KeyError",
        "AttributeError", "ImportError", "RuntimeError",
    }

    # Collecte des noms utilisés
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Pour les appels comme `obj.method`, on ne peut pas facilement
            # savoir si `obj` est défini sans analyse sémantique.
            pass

    # Combiner imports + defined + builtins
    all_known = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                all_known.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                all_known.add(alias.asname or alias.name)

    all_known |= defined | builtins

    # Noms utilisés mais pas connus
    undefined = []
    for name in used:
        if name not in all_known:
            # Filtrer les noms courants qui pourraient venir d'un contexte
            if name.startswith("_"):
                continue
            undefined.append(name)

    return sorted(undefined)


def analyze_file(filepath):
    """Analyse un fichier middleware."""
    rel_path = os.path.relpath(filepath, BASE_DIR)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Vérifier la syntaxe
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        return {
            "path": rel_path,
            "syntax_error": f"Ligne {e.lineno}: {e.msg}",
            "missing_imports": [],
            "undefined": [],
            "status": "error",
        }

    # 2. Imports manquants
    imported_names = get_imported_names(tree)
    missing = find_missing_imports(filepath, tree, content, imported_names)

    # 3. Noms indéfinis (approximatif)
    undefined = find_undefined_names(tree)
    # Filtrer les faux positifs (attributs de classes, etc.)
    undefined = [u for u in undefined if len(u) > 1]

    return {
        "path": rel_path,
        "syntax_error": None,
        "missing_imports": missing,
        "undefined": undefined,
        "status": "ok" if not missing and not undefined else "warning",
    }


def main():
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  ANALYSE DES MIDDLEWARES{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")

    files = find_middleware_files()

    if not files:
        print(f"  {YELLOW}Aucun fichier middleware trouvé dans apps/{RESET}")
        return

    print(f"  {len(files)} fichier(s) middleware trouvé(s)\n")

    all_ok = True
    for filepath in sorted(files):
        result = analyze_file(filepath)

        print(f"  {BOLD}📄 {result['path']}{RESET}")

        if result["syntax_error"]:
            print(f"     {RED}❌ Erreur de syntaxe : {result['syntax_error']}{RESET}")
            all_ok = False
        else:
            if result["missing_imports"]:
                print(f"     {RED}❌ Imports manquants : {', '.join(result['missing_imports'])}{RESET}")
                print(f"        → Ajoutez : {', '.join(f'import {m}' for m in result['missing_imports'])}")
                all_ok = False
            else:
                print(f"     {GREEN}✅ Imports OK{RESET}")

            if result["undefined"]:
                print(f"     {YELLOW}⚠️  Noms potentiellement indéfinis : {', '.join(result['undefined'][:10])}{RESET}")
                if len(result["undefined"]) > 10:
                    print(f"        ... et {len(result['undefined']) - 10} autres")

        print()

    # Résumé
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
    if all_ok:
        print(f"  {GREEN}{BOLD}🎉 TOUS LES MIDDLEWARES SONT VALIDES{RESET}")
    else:
        print(f"  {RED}{BOLD}⚠️  DES PROBLÈMES ONT ÉTÉ DÉTECTÉS{RESET}")
        print(f"\n  {YELLOW}Ajoutez les imports manquants en haut de chaque fichier.{RESET}")
        print(f"  {YELLOW}Puis testez à nouveau : python check_middlewares.py{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")

    # Bonus : vérifier les middlewares chargés par Django
    print(f"{BOLD}📋 Middlewares chargés par Django :{RESET}\n")
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        import django
        django.setup()
        from django.conf import settings
        for mw in settings.MIDDLEWARE:
            marker = "  "
            if mw.startswith("apps."):
                marker = f"  {CYAN}[custom]{RESET}"
            print(f"{marker} {mw}")
    except Exception as e:
        print(f"  {YELLOW}Impossible de charger Django : {e}{RESET}")

    print()


if __name__ == "__main__":
    main()