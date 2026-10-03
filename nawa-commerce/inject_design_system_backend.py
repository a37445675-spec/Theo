"""
Injection automatique du module Design System - Backend Django.
Crée tous les fichiers du module et configure le projet.

Usage : python inject_design_system_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "design_system")
SETTINGS_PATH = None
URLS_PATH = None


# ===== Contenu des fichiers =====
MODELS_PY = '''"""Modèles pour le Design System (couleurs, typographie, formes)."""
from django.core.validators import RegexValidator
from django.db import models


HEX_VALIDATOR = RegexValidator(
    regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
    message="Entrez une couleur hexadécimale valide (ex: #C1652F)."
)


class DesignSystem(models.Model):
    """Configuration globale du design (une seule instance active)."""

    name = models.CharField(max_length=100, default="NAWA Design System")
    is_active = models.BooleanField(default=True, help_text="Un seul design system peut être actif à la fois.")

    # === COULEURS ===
    color_primary = models.CharField(max_length=7, default="#C1652F", validators=[HEX_VALIDATOR], verbose_name="Couleur primaire")
    color_secondary = models.CharField(max_length=7, default="#2F4A3C", validators=[HEX_VALIDATOR], verbose_name="Couleur secondaire")
    color_background = models.CharField(max_length=7, default="#F7F0E4", validators=[HEX_VALIDATOR], verbose_name="Fond de page")
    color_surface = models.CharField(max_length=7, default="#FFFFFF", validators=[HEX_VALIDATOR], verbose_name="Surface (cartes)")
    color_text = models.CharField(max_length=7, default="#221B15", validators=[HEX_VALIDATOR], verbose_name="Texte principal")
    color_text_muted = models.CharField(max_length=7, default="#6B6259", validators=[HEX_VALIDATOR], verbose_name="Texte secondaire")
    color_accent = models.CharField(max_length=7, default="#D4A843", validators=[HEX_VALIDATOR], verbose_name="Couleur d'accent (or)")
    color_error = models.CharField(max_length=7, default="#DC2626", validators=[HEX_VALIDATOR], verbose_name="Erreur")
    color_success = models.CharField(max_length=7, default="#16A34A", validators=[HEX_VALIDATOR], verbose_name="Succès")

    # === TYPOGRAPHIE ===
    font_heading = models.CharField(max_length=100, default="Fraunces", verbose_name="Police des titres", help_text="Nom de la police Google Fonts (ex: Fraunces).")
    font_body = models.CharField(max_length=100, default="Sora", verbose_name="Police du corps", help_text="Nom de la police Google Fonts (ex: Sora, Inter).")
    font_size_base = models.CharField(max_length=20, default="16px", verbose_name="Taille de base")
    font_size_h1 = models.CharField(max_length=20, default="3.5rem", verbose_name="Taille H1")
    font_size_h2 = models.CharField(max_length=20, default="2.5rem", verbose_name="Taille H2")
    font_size_h3 = models.CharField(max_length=20, default="1.75rem", verbose_name="Taille H3")
    line_height = models.CharField(max_length=10, default="1.6", verbose_name="Hauteur de ligne")

    # === FORMES ===
    border_radius = models.CharField(max_length=20, default="16px", verbose_name="Rayon des bordures")
    button_radius = models.CharField(max_length=20, default="999px", verbose_name="Rayon des boutons")
    card_radius = models.CharField(max_length=20, default="16px", verbose_name="Rayon des cartes")

    # === OMBRES ===
    shadow_sm = models.CharField(max_length=100, default="0 1px 2px rgba(0,0,0,0.05)", verbose_name="Ombre petite")
    shadow_md = models.CharField(max_length=100, default="0 4px 12px rgba(0,0,0,0.10)", verbose_name="Ombre moyenne")
    shadow_lg = models.CharField(max_length=100, default="0 10px 30px rgba(0,0,0,0.15)", verbose_name="Ombre grande")

    # === AVANCÉ ===
    custom_css = models.TextField(blank=True, verbose_name="CSS personnalisé", help_text="CSS additionnel injecté dans le <head> (avancé).")

    # === MÉTADONNÉES ===
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Design System"
        verbose_name_plural = "Design System"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            DesignSystem.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        obj = cls.objects.filter(is_active=True).first()
        if not obj:
            obj = cls.objects.create()
        return obj
'''

SERIALIZERS_PY = '''"""Serializers DRF pour le Design System."""
from rest_framework import serializers
from .models import DesignSystem


class DesignSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystem
        fields = "__all__"
'''

VIEWS_PY = '''"""Vues API pour le Design System."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import DesignSystem
from .serializers import DesignSystemSerializer


class DesignSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint en lecture seule pour le Design System."""
    queryset = DesignSystem.objects.all()
    serializer_class = DesignSystemSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def active(self, request):
        obj = DesignSystem.get_active()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
'''

URLS_PY = '''"""URLs pour le Design System."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DesignSystemViewSet

router = DefaultRouter()
router.register(r"", DesignSystemViewSet, basename="design-system")

urlpatterns = [
    path("", include(router.urls)),
]
'''

ADMIN_PY = '''"""Admin Django pour le Design System."""
from django.contrib import admin
from django.utils.html import format_html
from .models import DesignSystem


@admin.register(DesignSystem)
class DesignSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "color_preview", "is_active", "updated_at")
    list_filter = ("is_active",)
    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Informations générales", {"fields": ("name", "is_active")}),
        ("Couleurs", {"fields": (
            "color_primary", "color_secondary", "color_accent",
            "color_background", "color_surface",
            "color_text", "color_text_muted",
            "color_error", "color_success",
        )}),
        ("Typographie", {"fields": (
            "font_heading", "font_body", "font_size_base",
            "font_size_h1", "font_size_h2", "font_size_h3", "line_height",
        )}),
        ("Formes", {"fields": ("border_radius", "button_radius", "card_radius")}),
        ("Ombres", {"fields": ("shadow_sm", "shadow_md", "shadow_lg")}),
        ("Avancé", {"fields": ("custom_css",), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("updated_at",)}),
    )

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:50%;vertical-align:middle;"></span> '
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:50%;vertical-align:middle;margin-left:4px;"></span>',
            obj.color_primary, obj.color_accent
        )
    color_preview.short_description = "Aperçu"
'''

APPS_PY = '''"""Configuration de l'application Design System."""
from django.apps import AppConfig


class DesignSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.design_system"
    verbose_name = "Design System"
'''

SEED_CMD_PY = '''"""Crée un Design System par défaut."""
from django.core.management.base import BaseCommand
from apps.design_system.models import DesignSystem


class Command(BaseCommand):
    help = "Crée le Design System par défaut NAWA."

    def handle(self, *args, **options):
        if DesignSystem.objects.exists():
            self.stdout.write(self.style.WARNING("Un Design System existe déjà."))
            return

        DesignSystem.objects.create(
            name="NAWA Design System",
            is_active=True,
            color_primary="#C1652F",
            color_secondary="#2F4A3C",
            color_background="#F7F0E4",
            color_surface="#FFFFFF",
            color_text="#221B15",
            color_text_muted="#6B6259",
            color_accent="#D4A843",
            color_error="#DC2626",
            color_success="#16A34A",
            font_heading="Fraunces",
            font_body="Sora",
            font_size_base="16px",
            font_size_h1="3.5rem",
            font_size_h2="2.5rem",
            font_size_h3="1.75rem",
            line_height="1.6",
        )
        self.stdout.write(self.style.SUCCESS("[OK] Design System créé avec succès."))
'''


# ===== Fonctions =====

def find_settings():
    for candidate in [
        os.path.join(BASE_DIR, "config", "settings.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "settings.py"),
        os.path.join(BASE_DIR, "core", "settings.py"),
    ]:
        if os.path.exists(candidate):
            return candidate
    for root, dirs, files in os.walk(BASE_DIR):
        if any(skip in root for skip in ("venv", ".venv", "node_modules", "apps")):
            continue
        if "settings.py" in files:
            return os.path.join(root, "settings.py")
    return None


def find_urls():
    for candidate in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
        os.path.join(BASE_DIR, "core", "urls.py"),
    ]:
        if os.path.exists(candidate):
            return candidate
    return None


def write_file(path, content, label=None):
    """Écrit le contenu dans un fichier (avec backup si existant)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = label or os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing.strip() == content.strip():
            print(f"  [SKIP] {label} (déjà à jour)")
            return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def ensure_init(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
        print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def ensure_installed_app():
    """Ajoute apps.design_system dans INSTALLED_APPS."""
    if not SETTINGS_PATH:
        print("  [ERREUR] settings.py introuvable.")
        return False

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if '"apps.design_system"' in content or "'apps.design_system'" in content:
        print("  [SKIP] apps.design_system déjà dans INSTALLED_APPS")
        return True

    shutil.copy2(SETTINGS_PATH, SETTINGS_PATH + ".bak")

    # Chercher INSTALLED_APPS sous toutes ses formes
    pattern = re.compile(r"INSTALLED_APPS\s*[:=]\s*[\[\(](.*?)[\]\)]", re.DOTALL)
    match = pattern.search(content)

    if not match:
        # Chercher dans un fichier séparé
        print("  [ATTENTION] INSTALLED_APPS introuvable dans ce fichier.")
        print("              Cherchez 'INSTALLED_APPS' dans votre projet.")
        return False

    block = match.group(1)
    # Trouver la fermeture
    closing_char = "]" if content[match.end() - 1] == "]" else ")"

    insertion = '    # === Design System ===\n    "apps.design_system",\n'
    new_block = block.rstrip() + "\n" + insertion + "    "

    new_content = content[:match.start(1)] + new_block + content[match.end(1):]

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] apps.design_system ajouté à INSTALLED_APPS")
    return True


def ensure_url():
    """Ajoute la route design-system dans urls.py."""
    if not URLS_PATH:
        print("  [ERREUR] urls.py introuvable.")
        return False

    with open(URLS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.design_system.urls" in content:
        print("  [SKIP] route design-system déjà présente")
        return True

    shutil.copy2(URLS_PATH, URLS_PATH + ".bak")

    pattern = re.compile(r"urlpatterns\s*=\s*\[(.*?)\]", re.DOTALL)
    match = pattern.search(content)

    if not match:
        print("  [ATTENTION] urlpatterns introuvable. Ajoutez la route manuellement :")
        print('              path("api/v1/design-system/", include("apps.design_system.urls")),')
        return False

    insertion = '\n    # === Design System ===\n    path("api/v1/design-system/", include("apps.design_system.urls")),\n'
    new_block = match.group(1).rstrip() + insertion
    new_content = content[:match.start(1)] + new_block + content[match.end(1):]

    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] route design-system ajoutée à urls.py")
    return True


def run_django_cmds():
    print("\n--- Migrations & Seed ---")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations", "design_system"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        subprocess.run([sys.executable, "manage.py", "seed_design_system"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")


def main():
    global SETTINGS_PATH, URLS_PATH

    print("=" * 60)
    print("  INJECTION DESIGN SYSTEM - BACKEND")
    print("=" * 60)

    SETTINGS_PATH = find_settings()
    URLS_PATH = find_urls()
    print(f"\n  settings.py : {SETTINGS_PATH}")
    print(f"  urls.py     : {URLS_PATH}")

    print("\n1. Création des fichiers de l'app...")
    ensure_init(os.path.join(APP_DIR, "__init__.py"))
    ensure_init(os.path.join(APP_DIR, "migrations", "__init__.py"))
    ensure_init(os.path.join(APP_DIR, "management", "__init__.py"))
    ensure_init(os.path.join(APP_DIR, "management", "commands", "__init__.py"))

    write_file(os.path.join(APP_DIR, "models.py"), MODELS_PY)
    write_file(os.path.join(APP_DIR, "serializers.py"), SERIALIZERS_PY)
    write_file(os.path.join(APP_DIR, "views.py"), VIEWS_PY)
    write_file(os.path.join(APP_DIR, "urls.py"), URLS_PY)
    write_file(os.path.join(APP_DIR, "admin.py"), ADMIN_PY)
    write_file(os.path.join(APP_DIR, "apps.py"), APPS_PY)
    write_file(
        os.path.join(APP_DIR, "management", "commands", "seed_design_system.py"),
        SEED_CMD_PY,
    )

    print("\n2. Vérification de settings.py...")
    ensure_installed_app()

    print("\n3. Vérification de urls.py...")
    ensure_url()

    print("\n4. Migrations et seed...")
    run_django_cmds()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nTestez sur : http://127.0.0.1:8000/api/v1/design-system/active/")
    print("Admin     : http://127.0.0.1:8000/admin/design_system/designsystem/")


if __name__ == "__main__":
    main()