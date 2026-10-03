"""
Corrige le chargement de .env.production par decouple.

Usage : python fix_env_loading.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROD_SETTINGS = os.path.join(BASE_DIR, "config", "settings_production.py")
ENV_PROD = os.path.join(BASE_DIR, ".env.production")
ENV_DEFAULT = os.path.join(BASE_DIR, ".env")


def read_env_file(path):
    """Lit un fichier .env et retourne un dict."""
    if not os.path.exists(path):
        return {}
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                result[key.strip()] = value.strip()
    return result


def main():
    print("=" * 60)
    print("  CORRECTION DU CHARGEMENT .env")
    print("=" * 60)

    if not os.path.exists(PROD_SETTINGS):
        print(f"\n  ❌ settings_production.py introuvable")
        return

    # 1. Vérifier que .env.production existe
    if not os.path.exists(ENV_PROD):
        print(f"\n  ❌ .env.production introuvable")
        print("  → Créez-le d'abord avec : notepad .env.production")
        return

    env_values = read_env_file(ENV_PROD)

    # 2. Vérifier que SECRET_KEY est bien rempli
    secret = env_values.get("SECRET_KEY", "")
    if not secret or "changez" in secret.lower() or len(secret) < 50:
        print(f"\n  ⚠️  SECRET_KEY manquante ou trop courte ({len(secret)} car.)")
        print("\n  Générez-en une avec :")
        print('  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"')
        print("\n  Puis collez-la dans .env.production :")
        print("    SECRET_KEY=votre_cle_generee")
        return

    print(f"\n  ✅ SECRET_KEY trouvée ({len(secret)} caractères)")

    # 3. Copier .env.production → .env (pour que decouple le lise)
    if os.path.exists(ENV_DEFAULT):
        shutil.copy2(ENV_DEFAULT, ENV_DEFAULT + ".bak")
        print(f"  [BACKUP] .env → .env.bak")

    shutil.copy2(ENV_PROD, ENV_DEFAULT)
    print(f"  [OK] .env.production copié vers .env")

    # 4. Améliorer settings_production.py pour lire explicitement .env.production
    with open(PROD_SETTINGS, "r", encoding="utf-8") as f:
        content = f.read()

    if "AutoConfig" in content and ".env.production" in content:
        print("  [SKIP] settings_production.py déjà patché")
    else:
        # Ajouter l'import AutoConfig + le chargement explicite
        header_patch = '''from .settings import *  # noqa
from decouple import Config, RepositoryEnv
from pathlib import Path

# === Chargement explicite de .env.production ===
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env.production"

if ENV_FILE.exists():
    config = Config(RepositoryEnv(str(ENV_FILE)))
else:
    from decouple import config
'''
        # Remplacer la ligne d'import decouple
        content = content.replace(
            "from .settings import *  # noqa\nfrom decouple import config\n",
            header_patch,
        )

        if "RepositoryEnv" not in content:
            # Fallback : ajouter après l'import settings
            content = content.replace(
                "from .settings import *  # noqa\n",
                header_patch + "\n",
                1,
            )

        with open(PROD_SETTINGS, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] settings_production.py patché (lecture .env.production)")

    print()
    print("=" * 60)
    print("  ✅ CORRECTION TERMINÉE")
    print("=" * 60)
    print("\nTestez :")
    print("  $env:DJANGO_SETTINGS_MODULE = 'config.settings_production'")
    print("  python manage.py check")
    print("  python check_production.py")


if __name__ == "__main__":
    main()