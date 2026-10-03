"""
Échafaudage de l'architecture Headless CMS - Backend Django.
Crée les applications, dossiers et fichiers pour les 12 modules du CMS.

Usage : python setup_cms_architecture.py
"""
import os
import shutil
import subprocess
import sys

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, "apps")
SETTINGS_PATH = None  # Détecté automatiquement
URLS_PATH = None       # Détecté automatiquement

# Liste des nouveaux modules (nom de dossier: libellé)
NEW_APPS = {
    "design_system": "Design System",
    "navigation": "Navigation & Menus",
    "seo": "SEO & Métadonnées",
    "translations": "Traductions",
    "feature_flags": "Feature Flags",
    "announcements": "Annonces & Bannières",
    "media_library": "Bibliothèque de médias",
    "shop_settings": "Configuration Boutique",
    "forms": "Formulaires dynamiques",
    "redirects": "Redirections",
    "third_party_scripts": "Scripts tiers",
    "email_templates": "Templates d'emails",
}

# Templates de fichiers
TEMPLATES = {
    "__init__.py": "",
    "models.py": '"""Modèles pour {label}."""\nfrom django.db import models\n\n# Les modèles seront ajoutés ici.\n',
    "views.py": '"""Vues API pour {label}."""\nfrom rest_framework import viewsets\n\n# Les vues seront ajoutées ici.\n',
    "serializers.py": '"""Serializers DRF pour {label}."""\nfrom rest_framework import serializers\n\n# Les serializers seront ajoutés ici.\n',
    "admin.py": '"""Admin Django pour {label}."""\nfrom django.contrib import admin\n\n# Les modèles seront enregistrés ici.\n',
    "urls.py": '"""URLs pour {label}."""\nfrom django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n# router.register(r"", MaVueViewSet)\n\nurlpatterns = [\n    path("", include(router.urls)),\n]\n',
    "apps.py": '"""Configuration de l\'application {label}."""\nfrom django.apps import AppConfig\n\n\nclass {class_name}Config(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "apps.{app_name}"\n    verbose_name = "{label}"\n',
    "migrations/__init__.py": "",
    "tests.py": '"""Tests pour {label}."""\nfrom django.test import TestCase\n\n# Les tests seront ajoutés ici.\n',
    "README.md": "# {label}\n\nModule du CMS Headless NAWA.\n",
}


def find_settings():
    """Trouve le fichier settings.py principal."""
    candidates = [
        os.path.join(BASE_DIR, "config", "settings.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "settings.py"),
        os.path.join(BASE_DIR, "core", "settings.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Recherche récursive si introuvable
    for root, dirs, files in os.walk(BASE_DIR):
        if "venv" in root or ".venv" in root or "node_modules" in root:
            continue
        if "settings.py" in files:
            return os.path.join(root, "settings.py")
    return None


def find_urls():
    """Trouve le fichier urls.py principal."""
    candidates = [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
        os.path.join(BASE_DIR, "core", "urls.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    for root, dirs, files in os.walk(BASE_DIR):
        if "venv" in root or ".venv" in root or "node_modules" in root:
            continue
        if "urls.py" in files and "apps" not in root.split(os.sep):
            return os.path.join(root, "urls.py")
    return None


def create_app(app_name, label):
    """Crée la structure complète d'une application Django."""
    app_dir = os.path.join(APPS_DIR, app_name)
    if os.path.exists(app_dir):
        print(f"  [EXISTE] apps/{app_name}/ (ignoré)")
        return False

    os.makedirs(os.path.join(app_dir, "migrations"), exist_ok=True)

    # Convertir "design_system" -> "DesignSystem"
    class_name = "".join(word.capitalize() for word in app_name.split("_"))

    for filename, template in TEMPLATES.items():
        file_path = os.path.join(app_dir, filename)
        if os.path.exists(file_path):
            continue
        content = template.format(
            label=label,
            app_name=app_name,
            class_name=class_name,
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"  [CRÉÉ] apps/{app_name}/")
    return True


def update_settings():
    """Ajoute les nouvelles apps à INSTALLED_APPS."""
    global SETTINGS_PATH
    if not SETTINGS_PATH or not os.path.exists(SETTINGS_PATH):
        print("  [ERREUR] settings.py introuvable. Ajoutez les apps manuellement.")
        return False

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérifier si déjà présentes
    apps_to_add = [f"apps.{app}" for app in NEW_APPS.keys()]
    if all(f'"{app}"' in content or f"'{app}'" in content for app in apps_to_add):
        print("  [INFO] Toutes les apps sont déjà dans INSTALLED_APPS.")
        return True

    shutil.copy2(SETTINGS_PATH, SETTINGS_PATH + ".bak")
    print(f"  [BACKUP] {SETTINGS_PATH}.bak")

    # Construire le bloc à insérer
    insert_lines = "\n    # === CMS Headless (ajoutés automatiquement) ===\n"
    for app in apps_to_add:
        if f'"{app}"' not in content and f"'{app}'" not in content:
            insert_lines += f'    "{app}",\n'

    # Trouver la fin de INSTALLED_APPS
    marker = "INSTALLED_APPS = ["
    if marker in content:
        # Insérer juste avant la fermeture du crochet de INSTALLED_APPS
        idx = content.index(marker)
        # Trouver la première occurrence de "]" après ce marker
        closing_idx = content.index("]", idx)
        content = content[:closing_idx] + insert_lines + content[closing_idx:]
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] {os.path.basename(SETTINGS_PATH)} mis à jour.")
        return True
    else:
        print(f"  [ATTENTION] INSTALLED_APPS introuvable dans {SETTINGS_PATH}.")
        return False


def update_urls():
    """Ajoute les routes des nouvelles apps dans urls.py."""
    global URLS_PATH
    if not URLS_PATH or not os.path.exists(URLS_PATH):
        print("  [ERREUR] urls.py principal introuvable.")
        return False

    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.design_system.urls" in content:
        print("  [INFO] Les routes CMS sont déjà dans urls.py.")
        return True

    shutil.copy2(URLS_PATH, URLS_PATH + ".bak")
    print(f"  [BACKUP] {URLS_PATH}.bak")

    # Construire les nouvelles routes
    routes = "\n    # === CMS Headless API ===\n"
    for app, label in NEW_APPS.items():
        # Route simplifiée : /api/v1/{app}/
        route_name = app.replace("_", "-")
        routes += f'    path("api/v1/{route_name}/", include("apps.{app}.urls")),\n'

    # Trouver la fin de urlpatterns
    marker = "urlpatterns = ["
    if marker in content:
        idx = content.index(marker)
        closing_idx = content.index("]", idx)
        content = content[:closing_idx] + routes + content[closing_idx:]
        with open(URLS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] {os.path.basename(URLS_PATH)} mis à jour.")
        return True
    else:
        print(f"  [ATTENTION] urlpatterns introuvable dans {URLS_PATH}.")
        return False


def create_apps_init():
    """Crée apps/__init__.py s'il n'existe pas."""
    init_path = os.path.join(APPS_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")
        print(f"  [CRÉÉ] {init_path}")


def run_migrations():
    """Lance les migrations (optionnel)."""
    print("\n--- Migrations Django ---")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] Migration échouée : {e}")


def main():
    global SETTINGS_PATH, URLS_PATH

    print("=" * 60)
    print("  ÉCHAFAUDAGE CMS HEADLESS - BACKEND")
    print("=" * 60)

    # Détecter les fichiers principaux
    print("\n0. Détection des fichiers de configuration...")
    SETTINGS_PATH = find_settings()
    URLS_PATH = find_urls()
    print(f"  settings.py : {SETTINGS_PATH or 'NON TROUVÉ'}")
    print(f"  urls.py     : {URLS_PATH or 'NON TROUVÉ'}")

    if not SETTINGS_PATH or not URLS_PATH:
        print("\n  [ERREUR] Impossible de trouver settings.py ou urls.py.")
        print("  Vérifiez la structure de votre projet.")
        sys.exit(1)

    # Créer les apps
    print("\n1. Création des applications...")
    create_apps_init()
    created = 0
    for app_name, label in NEW_APPS.items():
        if create_app(app_name, label):
            created += 1
    print(f"  → {created} nouvelle(s) app(s) créée(s).")

    # Mettre à jour settings.py
    print("\n2. Mise à jour de settings.py...")
    update_settings()

    # Mettre à jour urls.py
    print("\n3. Mise à jour de urls.py...")
    update_urls()

    # Migrations
    print("\n4. Exécution des migrations...")
    run_migrations()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nProchaines étapes :")
    print("  1. Vérifiez le 'git diff' pour voir les modifications")
    print("  2. Remplissez les modules un par un (models, views, serializers)")
    print("  3. Restaurez depuis les .bak en cas de problème")


if __name__ == "__main__":
    main()