"""Admin Django pour le SEO."""
from django.contrib import admin
from django.utils.html import format_html
from .models import SeoMetadata


@admin.register(SeoMetadata)
class SeoMetadataAdmin(admin.ModelAdmin):
    list_display = ("content_object_str", "meta_title_preview", "robots", "score", "updated_at")
    list_filter = ("robots", "og_type", "content_type")
    search_fields = ("meta_title", "meta_description", "content_object_str") if False else ("meta_title", "meta_description")
    readonly_fields = ("content_type", "object_id", "updated_at", "seo_preview")

    fieldsets = (
        ("Objet lié", {"fields": ("content_type", "object_id")}),
        ("Balises principales", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
        ("Open Graph", {"fields": ("og_title", "og_description", "og_image", "og_type")}),
        ("Twitter / X", {"fields": ("twitter_card",)}),
        ("Canonique & Robots", {"fields": ("canonical_url", "robots")}),
        ("Données structurées (JSON-LD)", {"fields": ("structured_data",)}),
        ("Métadonnées", {"fields": ("updated_at", "seo_preview")}),
    )

    def content_object_str(self, obj):
        try:
            return str(obj.content_object)
        except Exception:
            return "—"
    content_object_str.short_description = "Objet"

    def meta_title_preview(self, obj):
        return (obj.meta_title or "—")[:60]
    meta_title_preview.short_description = "Titre"

    def score(self, obj):
        """Score SEO basique (0-100)."""
        s = 0
        if obj.meta_title and 30 <= len(obj.meta_title) <= 70:
            s += 25
        if obj.meta_description and 100 <= len(obj.meta_description) <= 160:
            s += 25
        if obj.og_image:
            s += 25
        if obj.structured_data:
            s += 25
        color = "#16A34A" if s >= 75 else ("#D4A843" if s >= 50 else "#DC2626")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:4px;font-weight:600;">{}/100</span>',
            color, s
        )
    score.short_description = "Score SEO"

    def seo_preview(self, obj):
        return format_html(
            '<div style="border:1px solid #ddd;padding:12px;border-radius:8px;max-width:600px;">'
            '<div style="color:#1a0dab;font-size:18px;">{}</div>'
            '<div style="color:#006621;font-size:14px;">{}</div>'
            '<div style="color:#545454;font-size:13px;">{}</div>'
            '</div>',
            obj.meta_title or "(titre vide)",
            obj.canonical_url or "https://nawa.com/...",
            obj.meta_description or "(description vide)",
        )
    seo_preview.short_description = "Aperçu Google"
