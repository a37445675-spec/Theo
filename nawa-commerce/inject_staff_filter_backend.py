"""
Ajout du filtrage "Staff only" sur les items de menu - Backend.
Ajoute un champ 'visibility' au modèle MenuItem et met à jour le seed.

Usage : python inject_staff_filter_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "navigation")


# ============ NOUVEAU CONTENU DU MODÈLE ============

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

    # === Visibilité ===
    VISIBILITY_CHOICES = [
        ("all", "Tout le monde"),
        ("anonymous", "Visiteurs non connectés"),
        ("authenticated", "Utilisateurs connectés"),
        ("staff", "Staff (gestionnaires)"),
        ("superuser", "Superutilisateurs uniquement"),
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

    # === Filtrage par rôle ===
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="all",
        verbose_name="Visible par",
        help_text="Qui peut voir cet élément de menu ?"
    )

    # === Badge ===
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


# ============ NOUVEAU SEED ============

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
            # (label, url, order, visibility, badge_text, badge_color)
            ("Cosmétiques", "/boutique/cosmetiques", 0, "all", "", ""),
            ("Vêtements", "/boutique/vetements", 1, "all", "", ""),
            ("Chaussures", "/boutique/chaussures", 2, "all", "", ""),
            ("Électroménager", "/boutique/electromenager", 3, "all", "", ""),
            ("Journal", "/journal", 4, "all", "", ""),
            ("Gestion", "/gestion/commandes", 5, "staff", "Staff", "#2F4A3C"),
        ]
        for label, url, order, visibility, badge, color in header_items:
            MenuItem.objects.update_or_create(
                menu=header, label=label,
                defaults={
                    "url": url,
                    "order": order,
                    "is_visible": True,
                    "visibility": visibility,
                    "badge_text": badge,
                    "badge_color": color or "#C1652F",
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
            MenuItem.objects.update_or_create(
                menu=footer, label=label,
                defaults={"url": url, "order": order, "is_visible": True, "visibility": "all"}
            )
        self.stdout.write(f"  [OK] {len(footer_items)} items pour le Footer.")
        self.stdout.write(self.style.SUCCESS("\\n[SUCCESS] Menus de navigation générés."))
'''


# ============ ADMIN MIS À JOUR ============

ADMIN_PY = '''"""Admin Django pour la navigation."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = "menu"
    extra = 1
    fields = ("order", "label", "url", "icon", "parent", "visibility", "badge_text", "is_visible")
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
    list_display = ("label", "menu", "parent", "order", "visibility_badge", "badge_preview", "is_visible")
    list_filter = ("menu", "visibility", "is_visible")
    search_fields = ("label", "url")
    list_editable = ("order", "is_visible")
    ordering = ("menu", "order")

    def visibility_badge(self, obj):
        colors = {
            "all": "#6B6259",
            "anonymous": "#D4A843",
            "authenticated": "#16A34A",
            "staff": "#2F4A3C",
            "superuser": "#DC2626",
        }
        color = colors.get(obj.visibility, "#6B6259")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_visibility_display()
        )
    visibility_badge.short_description = "Visibilité"

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


# ============ FONCTIONS ============

def write_file(path, content):
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def run_cmd(*args):
    try:
        subprocess.run([sys.executable, "manage.py", *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("  FILTRAGE STAFF ONLY - BACKEND")
    print("=" * 60)

    print("\n1. Mise à jour de models.py (ajout du champ 'visibility')...")
    write_file(os.path.join(APP_DIR, "models.py"), MODELS_PY)

    print("\n2. Mise à jour de admin.py...")
    write_file(os.path.join(APP_DIR, "admin.py"), ADMIN_PY)

    print("\n3. Mise à jour du seed...")
    write_file(
        os.path.join(APP_DIR, "management", "commands", "seed_navigation.py"),
        SEED_CMD_PY,
    )

    print("\n4. Migration de la base de données...")
    run_cmd("makemigrations", "navigation")
    run_cmd("migrate")

    print("\n5. Ré-exécution du seed (met à jour les items existants)...")
    run_cmd("seed_navigation")

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nLe modèle MenuItem a maintenant un champ 'visibility'.")
    print("L'item 'Gestion' est marqué visibility='staff'.")
    print("\nProchain : mettez à jour DynamicMenu.jsx côté frontend (voir code fourni).")


if __name__ == "__main__":
    main()