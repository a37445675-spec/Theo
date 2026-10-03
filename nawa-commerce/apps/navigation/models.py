"""Modèles pour la navigation (menus, items, sous-items)."""
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
