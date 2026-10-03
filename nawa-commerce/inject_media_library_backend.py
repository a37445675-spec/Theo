"""
Injection du module Médiathèque - Backend Django.

Prérequis : l'app apps/media_library/ existe (créée par l'échafaudage).

Usage : python inject_media_library_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "media_library")


# ============================================================
#                    MODELS
# ============================================================

MODELS_PY = '''"""Modèles pour la médiathèque centralisée."""
import mimetypes
import os

from django.db import models
from django.utils.text import slugify
from PIL import Image


class MediaTag(models.Model):
    """Étiquette pour catégoriser les médias."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(max_length=7, default="#6B6259")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Étiquette média"
        verbose_name_plural = "Étiquettes média"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MediaAsset(models.Model):
    """
    Un média (image, vidéo, PDF...) uploadé une seule fois et réutilisable partout.
    Contient les métadonnées utiles pour le SEO et l'affichage.
    """

    FILE_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Vidéo"),
        ("pdf", "PDF"),
        ("document", "Document"),
        ("other", "Autre"),
    ]

    # === Fichier ===
    file = models.FileField(upload_to="media-library/%Y/%m/", verbose_name="Fichier")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="image")
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Taille en octets")

    # === Métadonnées ===
    name = models.CharField(max_length=200, verbose_name="Nom")
    alt_text = models.CharField(
        max_length=255, blank=True,
        verbose_name="Texte alternatif",
        help_text="Important pour le SEO et l'accessibilité."
    )
    caption = models.TextField(blank=True, verbose_name="Légende")

    # === Dimensions (uniquement pour les images) ===
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    # === Catégorisation ===
    tags = models.ManyToManyField(MediaTag, blank=True, related_name="assets")

    # === Métadonnées système ===
    uploaded_by = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="uploaded_media"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Média"
        verbose_name_plural = "Médiathèque"

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        # Détection automatique du type et de la taille
        if self.file:
            # MIME type
            if not self.mime_type:
                self.mime_type = mimetypes.guess_type(self.file.name)[0] or "application/octet-stream"

            # File size
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass

            # File type
            if not self.file_type or self.file_type == "other":
                if self.mime_type.startswith("image/"):
                    self.file_type = "image"
                elif self.mime_type.startswith("video/"):
                    self.file_type = "video"
                elif self.mime_type == "application/pdf":
                    self.file_type = "pdf"
                else:
                    self.file_type = "document"

            # Dimensions (pour les images)
            if self.file_type == "image" and (not self.width or not self.height):
                try:
                    with Image.open(self.file) as img:
                        self.width, self.height = img.size
                except Exception:
                    pass

        super().save(*args, **kwargs)

    @property
    def extension(self):
        return os.path.splitext(self.file.name)[1].lower().lstrip(".")

    @property
    def file_size_human(self):
        """Retourne la taille en Ko/Mo lisible."""
        size = self.file_size
        for unit in ["o", "Ko", "Mo", "Go"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"

    @property
    def ratio(self):
        if self.width and self.height:
            return round(self.width / self.height, 2)
        return None
'''


# ============================================================
#                    SERIALIZERS
# ============================================================

SERIALIZERS_PY = '''"""Serializers DRF pour la médiathèque."""
from rest_framework import serializers
from .models import MediaAsset, MediaTag


class MediaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaTag
        fields = ["id", "name", "slug", "color"]


class MediaAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    tags = MediaTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=MediaTag.objects.all(),
        source="tags", required=False
    )
    file_size_human = serializers.ReadOnlyField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id", "name", "alt_text", "caption",
            "file", "file_url", "thumbnail_url",
            "file_type", "mime_type", "file_size", "file_size_human",
            "width", "height",
            "tags", "tag_ids",
            "uploaded_by", "uploaded_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "file_type", "mime_type", "file_size",
            "width", "height", "uploaded_by",
            "created_at", "updated_at",
        ]
        extra_kwargs = {
            "file": {"required": True},
            "name": {"required": False},
        }

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def get_thumbnail_url(self, obj):
        """
        Retourne une URL de miniature.
        Si l'image est < 400px, on renvoie l'original.
        Sinon, on pourrait générer une miniature à la volée (via sorl-thumbnail par ex.).
        Pour l'instant, retourne l'original.
        """
        if not obj.file or obj.file_type != "image":
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None

    def create(self, validated_data):
        # Auto-nommer à partir du nom de fichier si non fourni
        if not validated_data.get("name"):
            validated_data["name"] = os.path.splitext(
                os.path.basename(validated_data["file"].name)
            )[0]
        return super().create(validated_data)


import os  # noqa: E402  (placé en bas pour lisibilité)
'''


# ============================================================
#                    VIEWS
# ============================================================

VIEWS_PY = '''"""Vues API pour la médiathèque."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q
from .models import MediaAsset, MediaTag
from .serializers import MediaAssetSerializer, MediaTagSerializer


class MediaTagViewSet(viewsets.ModelViewSet):
    """CRUD complet sur les étiquettes."""
    queryset = MediaTag.objects.all()
    serializer_class = MediaTagSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class MediaAssetViewSet(viewsets.ModelViewSet):
    """
    API Médiathèque.

    GET    /api/v1/media-library/assets/                   → liste paginée
    GET    /api/v1/media-library/assets/?file_type=image   → filtré par type
    GET    /api/v1/media-library/assets/?tag=produits      → filtré par tag
    GET    /api/v1/media-library/assets/?search=karité     → recherche nom + alt
    POST   /api/v1/media-library/assets/                   → upload (multipart)
    PATCH  /api/v1/media-library/assets/{id}/              → modifier les métadonnées
    DELETE /api/v1/media-library/assets/{id}/              → supprimer
    POST   /api/v1/media-library/assets/bulk-delete/       → supprimer plusieurs
    GET    /api/v1/media-library/assets/stats/             → statistiques
    """
    queryset = MediaAsset.objects.all().prefetch_related("tags")
    serializer_class = MediaAssetSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        file_type = self.request.query_params.get("file_type")
        if file_type:
            qs = qs.filter(file_type=file_type)

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(alt_text__icontains=search) |
                Q(caption__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(uploaded_by=user)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """Supprime plusieurs médias d'un coup. Body : {"ids": [1, 2, 3]}"""
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "Aucun ID fourni."},
                status=status.HTTP_400_BAD_REQUEST
            )
        deleted_count = MediaAsset.objects.filter(id__in=ids).delete()[0]
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Statistiques globales sur la médiathèque."""
        from django.db.models import Sum, Count
        total = MediaAsset.objects.count()
        by_type = list(
            MediaAsset.objects.values("file_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        total_size = MediaAsset.objects.aggregate(total=Sum("file_size"))["total"] or 0

        return Response({
            "total": total,
            "by_type": by_type,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        })
'''


# ============================================================
#                    URLS
# ============================================================

URLS_PY = '''"""URLs pour la médiathèque."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaAssetViewSet, MediaTagViewSet

router = DefaultRouter()
router.register(r"assets", MediaAssetViewSet, basename="media-asset")
router.register(r"tags", MediaTagViewSet, basename="media-tag")

urlpatterns = [
    path("", include(router.urls)),
]
'''


# ============================================================
#                    ADMIN
# ============================================================

ADMIN_PY = '''"""Admin Django pour la médiathèque (galerie visuelle)."""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import MediaAsset, MediaTag


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_preview", "asset_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:4px;vertical-align:middle;"></span>',
            obj.color
        )
    color_preview.short_description = "Couleur"

    def asset_count(self, obj):
        return obj.assets.count()
    asset_count.short_description = "Médias"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail_preview", "name", "file_type_badge",
        "dimensions", "file_size_human", "tags_list", "created_at"
    )
    list_filter = ("file_type", "tags", "created_at")
    search_fields = ("name", "alt_text", "caption")
    readonly_fields = (
        "file_type", "mime_type", "file_size",
        "width", "height", "uploaded_by",
        "created_at", "updated_at",
        "preview_large",
    )
    filter_horizontal = ("tags",)
    list_per_page = 30

    fieldsets = (
        ("Aperçu", {
            "fields": ("preview_large",)
        }),
        ("Fichier", {
            "fields": ("file", "file_type", "mime_type", "file_size", "width", "height")
        }),
        ("Métadonnées", {
            "fields": ("name", "alt_text", "caption", "tags")
        }),
        ("Système", {
            "fields": ("uploaded_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.file_type == "image" and obj.file:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;'
                'object-fit:cover;border-radius:8px;border:1px solid #eee;" />',
                obj.file.url
            )
        icons = {"video": "🎬", "pdf": "📄", "document": "📁", "other": "📎"}
        return format_html(
            '<span style="font-size:30px;">{}</span>',
            icons.get(obj.file_type, "📎")
        )
    thumbnail_preview.short_description = "Vignette"

    def preview_large(self, obj):
        if not obj.pk or not obj.file:
            return "Aucun fichier"
        if obj.file_type == "image":
            return format_html(
                '<img src="{}" style="max-width:400px;max-height:400px;'
                'border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.1);" />',
                obj.file.url
            )
        return format_html(
            '<a href="{}" target="_blank" style="padding:8px 16px;'
            'background:#C1652F;color:#fff;border-radius:6px;text-decoration:none;">'
            'Télécharger le fichier</a>',
            obj.file.url
        )
    preview_large.short_description = "Aperçu"

    def file_type_badge(self, obj):
        colors = {
            "image": "#16A34A", "video": "#DC2626",
            "pdf": "#D4A843", "document": "#2F4A3C", "other": "#6B6259",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;text-transform:uppercase;">{}</span>',
            colors.get(obj.file_type, "#6B6259"),
            obj.get_file_type_display()
        )
    file_type_badge.short_description = "Type"

    def dimensions(self, obj):
        if obj.width and obj.height:
            return f"{obj.width} × {obj.height}"
        return "—"
    dimensions.short_description = "Dimensions"

    def tags_list(self, obj):
        tags = obj.tags.all()
        if not tags:
            return "—"
        return format_html(" ".join([
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:999px;font-size:11px;margin-right:4px;">{}</span>'.format(
                t.color, t.name
            ) for t in tags
        ]))
    tags_list.short_description = "Étiquettes"

    def changelist_view(self, request, extra_context=None):
        """Injecte le total de la médiathèque dans le contexte."""
        extra_context = extra_context or {}
        extra_context["media_stats"] = MediaAsset.objects.aggregate(
            total=Count("id")
        )
        return super().changelist_view(request, extra_context=extra_context)
'''


# ============================================================
#                    APPS
# ============================================================

APPS_PY = '''"""Configuration de l'application Médiathèque."""
from django.apps import AppConfig


class MediaLibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.media_library"
    verbose_name = "Médiathèque"
'''


# ============================================================
#                    SEED
# ============================================================

SEED_PY = '''"""Crée des étiquettes de démonstration pour la médiathèque."""
from django.core.management.base import BaseCommand
from apps.media_library.models import MediaTag


DEFAULT_TAGS = [
    ("Produits", "#C1652F"),
    ("Bannières", "#2F4A3C"),
    ("Blog", "#D4A843"),
    ("Avatars", "#6B6259"),
    ("Logos", "#221B15"),
    ("Lifestyle", "#8A4B26"),
    ("Cosmétiques", "#DC2626"),
    ("Mode", "#1E40AF"),
    ("Maison", "#16A34A"),
    ("Promos", "#F59E0B"),
]


class Command(BaseCommand):
    help = "Crée les étiquettes par défaut de la médiathèque."

    def handle(self, *args, **options):
        created = 0
        for name, color in DEFAULT_TAGS:
            _, was_created = MediaTag.objects.get_or_create(
                name=name, defaults={"color": color}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} nouvelle(s) étiquette(s) créée(s), "
            f"{len(DEFAULT_TAGS)} au total."
        ))
'''


# ============================================================
#                    UTILITAIRES
# ============================================================

def ensure_init(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
        print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def write_file(path, content, backup=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        if backup:
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


def add_to_settings():
    settings = find_settings()
    if not settings:
        print("  [ERREUR] settings.py introuvable.")
        return False

    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()

    if '"apps.media_library"' in content:
        print("  [SKIP] apps.media_library déjà déclarée")
        return True

    shutil.copy2(settings, settings + ".bak")

    m = None
    for name in ("LOCAL_APPS", "INSTALLED_APPS"):
        m = re.search(rf"{name}\s*[:=]\s*\[(.*?)\]", content, re.DOTALL)
        if m:
            break

    if not m:
        print("  [ATTENTION] LOCAL_APPS introuvable.")
        return False

    insertion = '\n    "apps.media_library",\n'
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(settings, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] apps.media_library ajoutée à LOCAL_APPS")
    return True


def add_url_route():
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return False

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.media_library.urls" in content:
        print("  [SKIP] route déjà présente")
        return True

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        return False

    insertion = '\n    # === Médiathèque ===\n    path("api/v1/media-library/", include("apps.media_library.urls")),\n'
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] route /api/v1/media-library/ ajoutée")
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
    print("  INJECTION MÉDIATHÈQUE - BACKEND")
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
    write_file(
        os.path.join(APP_DIR, "management", "commands", "seed_media_tags.py"),
        SEED_PY,
    )

    print("\n2. Mise à jour de settings.py...")
    add_to_settings()

    print("\n3. Mise à jour de urls.py...")
    add_url_route()

    print("\n4. Migrations...")
    run_cmd("makemigrations", "media_library", allow_fail=True)
    run_cmd("migrate")

    print("\n5. Seed des étiquettes...")
    run_cmd("seed_media_tags", allow_fail=True)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nEndpoints :")
    print("  Assets : http://127.0.0.1:8000/api/v1/media-library/assets/")
    print("  Tags   : http://127.0.0.1:8000/api/v1/media-library/tags/")
    print("  Stats  : http://127.0.0.1:8000/api/v1/media-library/assets/stats/")
    print("\nAdmin :")
    print("  Médiathèque : http://127.0.0.1:8000/admin/media_library/mediaasset/")
    print("  Étiquettes  : http://127.0.0.1:8000/admin/media_library/mediatag/")


if __name__ == "__main__":
    main()