"""
Injection des modules Feature Flags et Annonces - Backend Django.

Prérequis : les apps apps/feature_flags/ et apps/announcements/ existent
            (créées par le script d'échafaudage).

Usage : python inject_feature_flags_announcements_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FF_DIR = os.path.join(BASE_DIR, "apps", "feature_flags")
AN_DIR = os.path.join(BASE_DIR, "apps", "announcements")


# ============================================================
#                FEATURE FLAGS - FICHIERS
# ============================================================

FF_MODELS_PY = '''"""Modèles pour les Feature Flags (interrupteurs de fonctionnalités)."""
from django.db import models


class FeatureFlag(models.Model):
    """
    Un feature flag permet d'activer/désactiver une fonctionnalité
    depuis l'admin, sans redéployer le code.

    Exemples :
      - code="wishlist"       → active la liste de souhaits
      - code="reviews"        → active les avis clients
      - code="header_search"  → affiche la barre de recherche
      - code="guest_checkout" → autorise la commande sans compte
    """

    TARGET_AUDIENCE_CHOICES = [
        ("all", "Tout le monde"),
        ("authenticated", "Utilisateurs connectés"),
        ("staff", "Staff uniquement"),
        ("beta", "Bêta-testeurs"),
    ]

    code = models.SlugField(
        max_length=100, unique=True,
        help_text="Identifiant technique (ex: wishlist, reviews)."
    )
    name = models.CharField(max_length=200, verbose_name="Nom affiché")
    description = models.TextField(
        blank=True,
        help_text="Description de ce que fait ce flag."
    )
    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Activé",
        help_text="Activer la fonctionnalité dans le frontend."
    )
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        default="all",
        verbose_name="Audience cible",
        help_text="À qui s'applique ce flag ?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        status = "✅" if self.is_enabled else "❌"
        return f"{status} {self.code} — {self.name}"
'''

FF_SERIALIZERS_PY = '''"""Serializers DRF pour les Feature Flags."""
from rest_framework import serializers
from .models import FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = [
            "id", "code", "name", "description",
            "is_enabled", "target_audience",
        ]
'''

FF_VIEWS_PY = '''"""Vues API pour les Feature Flags."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import FeatureFlag
from .serializers import FeatureFlagSerializer


class FeatureFlagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/feature-flags/  → tous les flags
    GET /api/v1/feature-flags/{id}/ → un flag
    """
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Pas de pagination pour les flags
'''

FF_URLS_PY = '''"""URLs pour les Feature Flags."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeatureFlagViewSet

router = DefaultRouter()
router.register(r"", FeatureFlagViewSet, basename="feature-flag")

urlpatterns = [
    path("", include(router.urls)),
]
'''

FF_ADMIN_PY = '''"""Admin Django pour les Feature Flags."""
from django.contrib import admin
from django.utils.html import format_html
from .models import FeatureFlag


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status_badge", "target_audience", "updated_at")
    list_filter = ("is_enabled", "target_audience")
    search_fields = ("code", "name", "description")
    list_editable = ("is_enabled",)
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Identification", {
            "fields": ("code", "name", "description")
        }),
        ("Configuration", {
            "fields": ("is_enabled", "target_audience")
        }),
        ("Métadonnées", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def status_badge(self, obj):
        if obj.is_enabled:
            return format_html(
                '<span style="background:#16A34A;color:#fff;padding:3px 10px;'
                'border-radius:999px;font-size:11px;font-weight:600;">ACTIF</span>'
            )
        return format_html(
            '<span style="background:#DC2626;color:#fff;padding:3px 10px;'
            'border-radius:999px;font-size:11px;font-weight:600;">INACTIF</span>'
        )
    status_badge.short_description = "Statut"
'''

FF_APPS_PY = '''"""Configuration de l'application Feature Flags."""
from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.feature_flags"
    verbose_name = "Feature Flags"
'''

FF_SEED_PY = '''"""Crée les feature flags par défaut de NAWA."""
from django.core.management.base import BaseCommand
from apps.feature_flags.models import FeatureFlag


DEFAULT_FLAGS = [
    # (code, name, description, is_enabled, target_audience)
    ("wishlist", "Liste de souhaits",
     "Permet aux clients d'ajouter des produits à une liste de souhaits.", True, "authenticated"),
    ("reviews", "Avis clients",
     "Affiche les avis et notes sur les fiches produit.", True, "all"),
    ("header_search", "Recherche dans l'en-tête",
     "Affiche une barre de recherche dans le header.", True, "all"),
    ("guest_checkout", "Commande sans compte",
     "Autorise les visiteurs à commander sans créer de compte.", True, "all"),
    ("loyalty_program", "Programme de fidélité",
     "Active les points de fidélité et les récompenses.", True, "authenticated"),
    ("subscriptions", "Abonnements récurrents",
     "Active la vente par abonnement (livraison périodique).", False, "authenticated"),
    ("b2b_portal", "Portail B2B",
     "Active l'espace professionnel B2B avec tarifs dédiés.", False, "staff"),
    ("bookings", "Réservations",
     "Active la prise de rendez-vous pour les services.", False, "all"),
    ("pos_mode", "Mode Point de Vente",
     "Active l'interface de caisse pour les boutiques physiques.", False, "staff"),
    ("dark_mode", "Mode sombre",
     "Permet aux utilisateurs de basculer en thème sombre.", False, "all"),
]


class Command(BaseCommand):
    help = "Crée les feature flags par défaut."

    def handle(self, *args, **options):
        created_count = 0
        for code, name, desc, enabled, audience in DEFAULT_FLAGS:
            obj, created = FeatureFlag.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "is_enabled": enabled,
                    "target_audience": audience,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created_count} nouveau(x) flag(s) créé(s), "
            f"{len(DEFAULT_FLAGS)} au total."
        ))
'''


# ============================================================
#                 ANNONCES - FICHIERS
# ============================================================

AN_MODELS_PY = '''"""Modèles pour les Annonces et Bannières (promos, infos)."""
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    """
    Une annonce à afficher dans le site.
    Peut apparaître en haut de page, en bas, ou en popup central.
    """

    POSITION_CHOICES = [
        ("top_bar", "Bandeau supérieur"),
        ("bottom", "Bandeau inférieur"),
        ("popup", "Popup central"),
        ("floating", "Bulle flottante"),
    ]

    # === Contenu ===
    message = models.CharField(max_length=500, verbose_name="Message")
    link = models.URLField(blank=True, verbose_name="Lien")
    link_label = models.CharField(
        max_length=100, blank=True,
        verbose_name="Texte du lien",
        help_text="Ex: 'En savoir plus', 'Profiter de l\\'offre'"
    )

    # === Style ===
    background_color = models.CharField(
        max_length=7, default="#C1652F",
        verbose_name="Couleur de fond"
    )
    text_color = models.CharField(
        max_length=7, default="#FFFFFF",
        verbose_name="Couleur du texte"
    )
    icon = models.ImageField(
        upload_to="announcements/icons/",
        blank=True, null=True,
        verbose_name="Icône (optionnelle)"
    )

    # === Ciblage ===
    position = models.CharField(
        max_length=20, choices=POSITION_CHOICES,
        default="top_bar", verbose_name="Position"
    )
    target_audience = models.CharField(
        max_length=20, default="all",
        choices=[
            ("all", "Tout le monde"),
            ("anonymous", "Visiteurs non connectés"),
            ("authenticated", "Utilisateurs connectés"),
        ],
        verbose_name="Audience cible"
    )
    target_pages = models.CharField(
        max_length=500, blank=True,
        verbose_name="Pages ciblées",
        help_text="Vide = toutes les pages. Sinon, URLs séparées par des virgules (ex: /, /boutique/cosmetiques)."
    )

    # === Programmation ===
    starts_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Début (optionnel)"
    )
    ends_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fin (optionnel)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activée"
    )

    # === Ordre ===
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Priorité",
        help_text="Plus petit = affiché en premier."
    )

    # === Métadonnées ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"

    def __str__(self):
        return f"{self.message[:60]} ({self.get_position_display()})"

    @property
    def is_currently_active(self):
        """Vérifie si l'annonce est active ET dans sa plage de dates."""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True
'''

AN_SERIALIZERS_PY = '''"""Serializers DRF pour les Annonces."""
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id", "message", "link", "link_label",
            "background_color", "text_color",
            "icon", "icon_url",
            "position", "target_audience", "target_pages",
            "starts_at", "ends_at", "is_active", "order",
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None
'''

AN_VIEWS_PY = '''"""Vues API pour les Annonces."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/announcements/                       → toutes les annonces actives
    GET /api/v1/announcements/?position=top_bar      → filtrées par position
    GET /api/v1/announcements/?position=popup        → popup
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Announcement.objects.filter(is_active=True)
        position = self.request.query_params.get("position")
        if position:
            qs = qs.filter(position=position)
        return qs
'''

AN_URLS_PY = '''"""URLs pour les Annonces."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet

router = DefaultRouter()
router.register(r"", AnnouncementViewSet, basename="announcement")

urlpatterns = [
    path("", include(router.urls)),
]
'''

AN_ADMIN_PY = '''"""Admin Django pour les Annonces."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "preview", "position", "target_audience",
        "status_badge", "schedule", "order"
    )
    list_filter = ("position", "is_active", "target_audience")
    search_fields = ("message", "link")
    list_editable = ("order",)
    ordering = ("order", "-created_at")

    fieldsets = (
        ("Contenu", {
            "fields": ("message", "link", "link_label")
        }),
        ("Style", {
            "fields": ("background_color", "text_color", "icon")
        }),
        ("Ciblage", {
            "fields": ("position", "target_audience", "target_pages")
        }),
        ("Programmation", {
            "fields": ("starts_at", "ends_at", "is_active", "order")
        }),
    )

    def preview(self, obj):
        return format_html(
            '<span style="background:{};color:{};padding:4px 10px;'
            'border-radius:6px;font-size:12px;">{}</span>',
            obj.background_color, obj.text_color, obj.message[:60]
        )
    preview.short_description = "Aperçu"

    def status_badge(self, obj):
        if not obj.is_active:
            return format_html(
                '<span style="background:#888;color:#fff;padding:3px 10px;'
                'border-radius:999px;font-size:11px;">INACTIVE</span>'
            )
        if obj.is_currently_active:
            return format_html(
                '<span style="background:#16A34A;color:#fff;padding:3px 10px;'
                'border-radius:999px;font-size:11px;">ACTIVE</span>'
            )
        return format_html(
            '<span style="background:#D4A843;color:#fff;padding:3px 10px;'
            'border-radius:999px;font-size:11px;">PROGRAMMÉE</span>'
        )
    status_badge.short_description = "Statut"

    def schedule(self, obj):
        if not obj.starts_at and not obj.ends_at:
            return "—"
        start = obj.starts_at.strftime("%d/%m/%Y") if obj.starts_at else "?"
        end = obj.ends_at.strftime("%d/%m/%Y") if obj.ends_at else "?"
        return f"{start} → {end}"
    schedule.short_description = "Planification"
'''

AN_APPS_PY = '''"""Configuration de l'application Annonces."""
from django.apps import AppConfig


class AnnouncementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.announcements"
    verbose_name = "Annonces & Bannières"
'''

AN_SEED_PY = '''"""Crée des annonces de démonstration."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.announcements.models import Announcement


class Command(BaseCommand):
    help = "Crée des annonces de démonstration."

    def handle(self, *args, **options):
        if Announcement.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Des annonces existent déjà. Étape ignorée."
            ))
            return

        now = timezone.now()

        Announcement.objects.create(
            message="🎉 Livraison offerte dès 49€ d'achat !",
            link="/boutique/cosmetiques",
            link_label="Découvrir",
            background_color="#C1652F",
            text_color="#FFFFFF",
            position="top_bar",
            target_audience="all",
            is_active=True,
            order=0,
        )

        Announcement.objects.create(
            message="✨ Nouvelle collection Wax disponible",
            link="/boutique/vetements",
            link_label="Voir la collection",
            background_color="#2F4A3C",
            text_color="#F7F0E4",
            position="top_bar",
            target_audience="all",
            is_active=True,
            order=1,
        )

        Announcement.objects.create(
            message="Bienvenue sur NAWA ! Profitez de -10% sur votre première commande.",
            link="/inscription",
            link_label="Créer un compte",
            background_color="#D4A843",
            text_color="#221B15",
            position="popup",
            target_audience="anonymous",
            is_active=True,
            order=0,
            starts_at=now,
            ends_at=now + timedelta(days=30),
        )

        self.stdout.write(self.style.SUCCESS(
            "[OK] 3 annonces de démonstration créées."
        ))
'''


# ============================================================
#                    FONCTIONS UTILITAIRES
# ============================================================

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
    ]:
        if os.path.exists(c):
            return c
    return None


def find_urls():
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def add_to_local_apps():
    settings = find_settings()
    if not settings:
        print("  [ERREUR] settings.py introuvable.")
        return False

    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()

    new_apps = []
    if '"apps.feature_flags"' not in content:
        new_apps.append("apps.feature_flags")
    if '"apps.announcements"' not in content:
        new_apps.append("apps.announcements")

    if not new_apps:
        print("  [SKIP] apps déjà déclarées dans settings.py")
        return True

    shutil.copy2(settings, settings + ".bak")

    target = None
    for name in ("LOCAL_APPS", "INSTALLED_APPS"):
        m = re.search(rf"{name}\s*[:=]\s*\[(.*?)\]", content, re.DOTALL)
        if m:
            target = (name, m)
            break

    if not target:
        print("  [ATTENTION] LOCAL_APPS/INSTALLED_APPS introuvable.")
        return False

    name, m = target
    insertion = "".join(f'\n    "{a}",' for a in new_apps) + "\n"
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(settings, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] {len(new_apps)} app(s) ajoutée(s) à {name}")
    return True


def add_url_routes(routes):
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return False

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    if all(route[1] in content for route in routes):
        print("  [SKIP] routes déjà présentes")
        return True

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        print("  [ATTENTION] urlpatterns introuvable.")
        return False

    insertion = "\n    # === Feature Flags & Annonces ===\n"
    for path, _, url_path in routes:
        if url_path not in content:
            insertion += f'    path("{url_path}", include("{path}")),\n'

    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] routes ajoutées")
    return True


def run_cmd(*args, allow_fail=False):
    try:
        subprocess.run([sys.executable, "manage.py", *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        if not allow_fail:
            sys.exit(1)


def main():
    print("=" * 60)
    print("  INJECTION FEATURE FLAGS + ANNONCES - BACKEND")
    print("=" * 60)

    # ---------- FEATURE FLAGS ----------
    print("\n1. Création des fichiers Feature Flags...")
    for sub in ["", "migrations", "management", "management/commands"]:
        ensure_init(os.path.join(FF_DIR, sub, "__init__.py"))
    write_file(os.path.join(FF_DIR, "models.py"), FF_MODELS_PY)
    write_file(os.path.join(FF_DIR, "serializers.py"), FF_SERIALIZERS_PY)
    write_file(os.path.join(FF_DIR, "views.py"), FF_VIEWS_PY)
    write_file(os.path.join(FF_DIR, "urls.py"), FF_URLS_PY)
    write_file(os.path.join(FF_DIR, "admin.py"), FF_ADMIN_PY)
    write_file(os.path.join(FF_DIR, "apps.py"), FF_APPS_PY)
    write_file(
        os.path.join(FF_DIR, "management", "commands", "seed_feature_flags.py"),
        FF_SEED_PY,
    )

    # ---------- ANNONCES ----------
    print("\n2. Création des fichiers Annonces...")
    for sub in ["", "migrations", "management", "management/commands"]:
        ensure_init(os.path.join(AN_DIR, sub, "__init__.py"))
    write_file(os.path.join(AN_DIR, "models.py"), AN_MODELS_PY)
    write_file(os.path.join(AN_DIR, "serializers.py"), AN_SERIALIZERS_PY)
    write_file(os.path.join(AN_DIR, "views.py"), AN_VIEWS_PY)
    write_file(os.path.join(AN_DIR, "urls.py"), AN_URLS_PY)
    write_file(os.path.join(AN_DIR, "admin.py"), AN_ADMIN_PY)
    write_file(os.path.join(AN_DIR, "apps.py"), AN_APPS_PY)
    write_file(
        os.path.join(AN_DIR, "management", "commands", "seed_announcements.py"),
        AN_SEED_PY,
    )

    # ---------- SETTINGS ----------
    print("\n3. Mise à jour de settings.py...")
    add_to_local_apps()

    # ---------- URLS ----------
    print("\n4. Mise à jour de urls.py...")
    add_url_routes([
        ("apps.feature_flags.urls", "feature-flags", "api/v1/feature-flags/"),
        ("apps.announcements.urls", "announcements", "api/v1/announcements/"),
    ])

    # ---------- MIGRATIONS ----------
    print("\n5. Migrations...")
    run_cmd("makemigrations", "feature_flags", "announcements", allow_fail=True)
    run_cmd("migrate")

    # ---------- SEEDS ----------
    print("\n6. Seeds...")
    run_cmd("seed_feature_flags", allow_fail=True)
    run_cmd("seed_announcements", allow_fail=True)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nEndpoints disponibles :")
    print("  Feature Flags : http://127.0.0.1:8000/api/v1/feature-flags/")
    print("  Annonces      : http://127.0.0.1:8000/api/v1/announcements/")
    print("  Top bar       : http://127.0.0.1:8000/api/v1/announcements/?position=top_bar")
    print("  Popup         : http://127.0.0.1:8000/api/v1/announcements/?position=popup")
    print("\nAdmin :")
    print("  Feature Flags : http://127.0.0.1:8000/admin/feature_flags/featureflag/")
    print("  Annonces      : http://127.0.0.1:8000/admin/announcements/announcement/")


if __name__ == "__main__":
    main()