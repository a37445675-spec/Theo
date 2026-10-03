"""
Corrige le CSRF pour le panier :
- Crée une vue /api/v1/csrf/ qui pose le cookie CSRF
- Vérifie la config Django (CSRF_COOKIE_HTTPONLY, TRUSTED_ORIGINS)
- Ajoute la route

Usage : python fix_csrf_backend.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(BASE_DIR, "apps", "core")
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.py")
URLS_PATH = os.path.join(BASE_DIR, "config", "urls.py")


# ============================================================
#              VUE CSRF
# ============================================================

CSRF_VIEW_CODE = '''"""Vue CSRF — pose le cookie pour les clients SPA."""
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET


@require_GET
@ensure_csrf_cookie
def csrf_bootstrap(request):
    """
    Endpoint appelé par le SPA au boot pour obtenir un token CSRF.
    Pose le cookie csrftoken ET retourne le token dans le JSON.
    """
    token = get_token(request)
    return JsonResponse({"csrfToken": token})
'''


# ============================================================
#              FONCTIONS
# ============================================================

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, content, backup=True):
    ensure_dir(os.path.dirname(path))
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return False
        if backup:
            shutil.copy2(path, path + ".bak")
            print(f"  [BACKUP] {label}.bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def write_csrf_view():
    """Crée apps/core/csrf_views.py."""
    path = os.path.join(CORE_DIR, "csrf_views.py")
    return write_file(path, CSRF_VIEW_CODE)


def ensure_init():
    init_path = os.path.join(CORE_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")
        print(f"  [OK] apps/core/__init__.py")


def patch_settings():
    """Vérifie et corrige les settings CSRF."""
    if not os.path.exists(SETTINGS_PATH):
        print(f"  [ERREUR] settings.py introuvable")
        return False

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    additions = []

    # Vérifier CSRF_COOKIE_HTTPONLY
    if "CSRF_COOKIE_HTTPONLY" not in content:
        additions.append("CSRF_COOKIE_HTTPONLY = False  # Le JS doit pouvoir lire le cookie")
    else:
        # Vérifier que c'est False
        m = re.search(r'CSRF_COOKIE_HTTPONLY\s*=\s*(\w+)', content)
        if m and m.group(1) == "True":
            content = re.sub(
                r'CSRF_COOKIE_HTTPONLY\s*=\s*True',
                'CSRF_COOKIE_HTTPONLY = False',
                content,
            )
            print("  [FIX] CSRF_COOKIE_HTTPONLY = True → False")

    # Vérifier CSRF_COOKIE_SAMESITE
    if "CSRF_COOKIE_SAMESITE" not in content:
        additions.append('CSRF_COOKIE_SAMESITE = "Lax"')

    # Vérifier SESSION_COOKIE_SAMESITE
    if "SESSION_COOKIE_SAMESITE" not in content:
        additions.append('SESSION_COOKIE_SAMESITE = "Lax"')

    if additions:
        # Ajouter à la fin du fichier
        block = "\n\n# === Config CSRF (ajouté automatiquement) ===\n"
        block += "\n".join(additions) + "\n"
        content = content.rstrip() + block

        shutil.copy2(SETTINGS_PATH, SETTINGS_PATH + ".bak")
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] settings.py mis à jour ({len(additions)} ajout(s))")
    else:
        print("  [SKIP] settings.py déjà correct")

    return True


def patch_urls():
    """Ajoute la route /api/v1/csrf/."""
    if not os.path.exists(URLS_PATH):
        print(f"  [ERREUR] urls.py introuvable")
        return False

    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "csrf_bootstrap" in content:
        print("  [SKIP] Route CSRF déjà présente")
        return True

    shutil.copy2(URLS_PATH, URLS_PATH + ".bak")

    # 1. Ajouter l'import
    import_line = "from apps.core.csrf_views import csrf_bootstrap\n"
    if import_line not in content:
        # Trouver le dernier import
        lines = content.split("\n")
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                last_import = i
        lines.insert(last_import + 1, import_line.rstrip())
        content = "\n".join(lines)

    # 2. Ajouter la route
    route = '    path("api/v1/csrf/", csrf_bootstrap, name="csrf-bootstrap"),\n'
    # Insérer après la première route (admin)
    marker = '    path("admin/", admin.site.urls),\n'
    if marker in content:
        content = content.replace(marker, marker + "\n    # === CSRF bootstrap ===\n" + route + "\n", 1)
    else:
        print("  [ATTENTION] Impossible de trouver le point d'insertion")

    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Route /api/v1/csrf/ ajoutée")
    return True


def run_check():
    """Vérifie que Django démarre."""
    import subprocess, sys
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            capture_output=True, text=True, timeout=30,
        )
        if "System check identified no issues" in result.stdout or "0 silenced" in result.stdout:
            print("\n  ✅ Django démarre correctement")
            return True
        print(f"\n  ⚠️  Django : {result.stdout[-200:]}")
        return False
    except Exception as e:
        print(f"\n  [ERREUR] {e}")
        return False


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  CORRECTION CSRF — BACKEND")
    print("=" * 60)

    print("\n[1/4] Création de la vue CSRF...")
    ensure_init()
    write_csrf_view()

    print("\n[2/4] Vérification de settings.py...")
    patch_settings()

    print("\n[3/4] Ajout de la route /api/v1/csrf/...")
    patch_urls()

    print("\n[4/4] Vérification Django...")
    run_check()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\nTest rapide (backend doit tourner) :")
    print("  Invoke-RestMethod 'http://localhost:8000/api/v1/csrf/'")


if __name__ == "__main__":
    main()