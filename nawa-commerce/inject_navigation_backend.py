"""
Injection automatique du module Navigation - Backend Django.
Crée les modèles Menu/MenuItem, l'API, l'admin et le seed.

Usage : python inject_navigation_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "navigation"
APP_DIR = os.path.join(BASE_DIR, "apps", APP_NAME)


# ============ CONTENU DES FICHIERS ============

MODELS_PY = '''"""Modèles pour la navigation (menus, items, sous-items)."""
from django.db import models


class Menu(models.Model):
    """Un menu (Header, Footer, Mobile)."""

    LOCATION_CHOICES = [
        ("header", "En-tête"),
        ("footer", "Pied de page"),
        ("mobile", "Menu mobile"),
        ("sidebar", "Barre latérale"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom du menu")
    slug = models.SlugField(max_length=100, unique=True, help_text="Identifiant technique (ex: header-main).")
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="header")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["location", "order", "name"]
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        return f"{self.name} ({self.get_location_display()})"


class MenuItem(models.Model):
    """Un élément de menu. Peut contenir des sous-items (children)."""

    TARGET_CHOICES = [
        ("_self", "Même onglet"),
        ("_blank", "Nouvel onglet"),
    ]

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="children"
    )
    label = models.CharField(max_length=100, verbose_name="Libellé")
    url = models.CharField(max_length=500, blank=True, verbose_name="URL", help_text="Lien relatif (/boutique) ou absolu (https://...).")
    icon = models.ImageField(upload_to="navigation/icons/", blank=True, null=True, verbose_name="Icône")
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default="_self")
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    # Métadonnées optionnelles
    badge_text = models.CharField(max_length=20, blank=True, verbose_name="Badge (ex: Nouveau)")
    badge_color = models.CharField(max_length=7, blank=True, default="#C1652F", verbose_name="Couleur du badge")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "label"]
        verbose_name = "Élément de menu"
        verbose_name_plural = "Éléments de menu"

    def __str__(self):
        return f"{self.label} ({self.menu.name})"
'''

SERIALIZERS_PY = '''"""Serializers DRF pour la navigation."""
from rest_framework import serializers
from .models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id", "label", "url", "icon", "icon_url", "target",
            "order", "is_visible", "badge_text", "badge_color",
            "children",
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None

    def get_children(self, obj):
        children = obj.children.filter(is_visible=True).order_by("order")
        return MenuItemSerializer(children, many=True, context=self.context).data


class MenuSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["id", "name", "slug", "location", "is_active", "order", "items"]

    def get_items(self, obj):
        # On ne prend que les items racine (parent=None)
        root_items = obj.items.filter(parent=None, is_visible=True).order_by("order")
        return MenuItemSerializer(root_items, many=True, context=self.context).data
'''

VIEWS_PY = '''"""Vues API pour la navigation."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Menu
from .serializers import MenuSerializer


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/navigation/menus/              → tous les menus actifs
    GET /api/v1/navigation/menus/?location=header → filtre par emplacement
    GET /api/v1/navigation/menus/{id}/         → détail d'un menu
    GET /api/v1/navigation/menus/by-slug/{slug}/ → récupération par slug
    """
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        qs = Menu.objects.filter(is_active=True).prefetch_related("items__children")
        location = self.request.query_params.get("location")
        if location:
            qs = qs.filter(location=location)
        return qs

    @action(detail=False, methods=["get"], url_path=r"by-slug/(?P<slug>[\\w-]+)")
    def by_slug(self, request, slug=None):
        menu = get_object_or_404(Menu, slug=slug, is_active=True)
        serializer = self.get_serializer(menu)
        return Response(serializer.data)
'''

URLS_PY = '''"""URLs pour la navigation."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet

router = DefaultRouter()
router.register(r"menus", MenuViewSet, basename="menu")

urlpatterns = [
    path("", include(router.urls)),
]
'''

ADMIN_PY = '''"""Admin Django pour la navigation."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = "menu"
    extra = 1
    fields = ("order", "label", "url", "icon", "parent", "badge_text", "is_visible")
    ordering = ("order",)
    classes = ("collapse",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "order", "item_count", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MenuItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Éléments"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("label", "menu", "parent", "order", "badge_preview", "is_visible")
    list_filter = ("menu", "is_visible")
    search_fields = ("label", "url")
    list_editable = ("order", "is_visible")
    ordering = ("menu", "order")

    def badge_preview(self, obj):
        if obj.badge_text:
            return format_html(
                '<span style="background:{};color:#fff;padding:2px 8px;'
                'border-radius:999px;font-size:11px;">{}</span>',
                obj.badge_color, obj.badge_text
            )
        return "—"
    badge_preview.short_description = "Badge"
'''

APPS_PY = '''"""Configuration de l'application Navigation."""
from django.apps import AppConfig


class NavigationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.navigation"
    verbose_name = "Navigation & Menus"
'''

SEED_CMD_PY = '''"""Crée les menus par défaut NAWA (Header + Footer)."""
from django.core.management.base import BaseCommand
from apps.navigation.models import Menu, MenuItem


class Command(BaseCommand):
    help = "Crée les menus Header et Footer par défaut."

    def handle(self, *args, **options):
        # ---- Menu Header ----
        header, created = Menu.objects.get_or_create(
            slug="header-main",
            defaults={
                "name": "Menu principal",
                "location": "header",
                "order": 0,
                "is_active": True,
            }
        )
        if created:
            self.stdout.write("  [OK] Menu 'header-main' créé.")
        else:
            self.stdout.write("  [SKIP] Menu 'header-main' existe déjà.")

        header_items = [
            ("Cosmétiques", "/boutique/cosmetiques", 0, ""),
            ("Vêtements", "/boutique/vetements", 1, ""),
            ("Chaussures", "/boutique/chaussures", 2, ""),
            ("Électroménager", "/boutique/electromenager", 3, ""),
            ("Journal", "/journal", 4, ""),
            ("Gestion", "/gestion/commandes", 5, "Staff"),
        ]
        for label, url, order, badge in header_items:
            MenuItem.objects.get_or_create(
                menu=header, label=label,
                defaults={
                    "url": url, "order": order, "is_visible": True,
                    "badge_text": badge,
                }
            )
        self.stdout.write(f"  [OK] {len(header_items)} items pour le Header.")

        # ---- Menu Footer ----
        footer, created = Menu.objects.get_or_create(
            slug="footer-main",
            defaults={
                "name": "Menu pied de page",
                "location": "footer",
                "order": 0,
                "is_active": True,
            }
        )
        if created:
            self.stdout.write("  [OK] Menu 'footer-main' créé.")

        footer_items = [
            ("À propos", "/a-propos", 0),
            ("Contact", "/contact", 1),
            ("CGV", "/cgv", 2),
            ("Mentions légales", "/mentions-legales", 3),
            ("Politique de confidentialité", "/confidentialite", 4),
            ("Retours & remboursements", "/retours", 5),
        ]
        for label, url, order in footer_items:
            MenuItem.objects.get_or_create(
                menu=footer, label=label,
                defaults={"url": url, "order": order, "is_visible": True}
            )
        self.stdout.write(f"  [OK] {len(footer_items)} items pour le Footer.")
        self.stdout.write(self.style.SUCCESS("\\n[SUCCESS] Menus de navigation générés."))
'''


# ============ FONCTIONS UTILITAIRES ============

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def ensure_init(path):
    ensure_dir(os.path.dirname(path))
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
        print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def write_file(path, content):
    ensure_dir(os.path.dirname(path))
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def find_settings():
    for c in [
        os.path.join(BASE_DIR, "config", "settings.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "settings.py"),
        os.path.join(BASE_DIR, "core", "settings.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def find_urls():
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
        os.path.join(BASE_DIR, "core", "urls.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def add_to_local_apps():
    """Ajoute apps.navigation dans LOCAL_APPS (ou INSTALLED_APPS)."""
    settings = find_settings()
    if not settings:
        print("  [ERREUR] settings.py introuvable.")
        return False

    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()

    if '"apps.navigation"' in content:
        print("  [SKIP] apps.navigation déjà dans settings.py")
        return True

    shutil.copy2(settings, settings + ".bak")

    # Chercher LOCAL_APPS en priorité, sinon INSTALLED_APPS
    target = None
    for name in ("LOCAL_APPS", "INSTALLED_APPS"):
        m = re.search(rf"{name}\s*[:=]\s*\[(.*?)\]", content, re.DOTALL)
        if m:
            target = (name, m)
            break

    if not target:
        print("  [ATTENTION] Impossible de trouver LOCAL_APPS ou INSTALLED_APPS.")
        print("              Ajoutez manuellement : \"apps.navigation\",")
        return False

    name, m = target
    block = m.group(1).rstrip()
    insertion = '\n    "apps.navigation",\n'
    new_block = block + insertion

    new_content = content[:m.start(1)] + new_block + content[m.end(1):]
    with open(settings, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] apps.navigation ajouté à {name}")
    return True


def add_url_route():
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return False

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.navigation.urls" in content:
        print("  [SKIP] route navigation déjà présente")
        return True

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        print("  [ATTENTION] urlpatterns introuvable.")
        return False

    insertion = '\n    # === Navigation ===\n    path("api/v1/navigation/", include("apps.navigation.urls")),\n'
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] route /api/v1/navigation/ ajoutée")
    return True


def run_migrations():
    print("\n--- Migrations & Seed ---")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations", APP_NAME], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        subprocess.run([sys.executable, "manage.py", "seed_navigation"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")


def main():
    print("=" * 60)
    print("  INJECTION NAVIGATION - BACKEND")
    print("=" * 60)

    print("\n1. Création des fichiers...")
    for sub in ["", "migrations", "management", "management/commands"]:
        ensure_init(os.path.join(APP_DIR, sub, "__init__.py"))
    write_file(os.path.join(APP_DIR, "models.py"), MODELS_PY)
    write_file(os.path.join(APP_DIR, "serializers.py"), SERIALIZERS_PY)
    write_file(os.path.join(APP_DIR, "views.py"), VIEWS_PY)
    write_file(os.path.join(APP_DIR, "urls.py"), URLS_PY)
    write_file(os.path.join(APP_DIR, "admin.py"), ADMIN_PY)
    write_file(os.path.join(APP_DIR, "apps.py"), APPS_PY)
    write_file(os.path.join(APP_DIR, "management", "commands", "seed_navigation.py"), SEED_CMD_PY)

    print("\n2. Mise à jour de settings.py...")
    add_to_local_apps()

    print("\n3. Mise à jour de urls.py...")
    add_url_route()

    print("\n4. Migrations et seed...")
    run_migrations()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nTestez : http://127.0.0.1:8000/api/v1/navigation/menus/")
    print("Admin  : http://127.0.0.1:8000/admin/navigation/menu/")


if __name__ == "__main__":
    main()