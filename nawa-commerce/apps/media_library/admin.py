"""Admin Django pour la médiathèque (galerie visuelle)."""
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
