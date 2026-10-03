"""Admin Django pour les traductions."""
from django.contrib import admin
from django.utils.html import format_html
from .models import TranslationKey


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "context", "preview_fr", "preview_en", "is_active", "updated_at")
    list_filter = ("context", "is_active")
    search_fields = ("key", "context", "description")
    list_editable = ("is_active",)
    ordering = ("key",)

    fieldsets = (
        ("Identification", {"fields": ("key", "context", "description")}),
        ("Traductions (JSON)", {
            "fields": ("values",),
            "description": 'Format attendu : {"fr": "Bonjour", "en": "Hello"}'
        }),
        ("Statut", {"fields": ("is_active",)}),
    )

    def preview_fr(self, obj):
        return (obj.values or {}).get("fr", "—")[:60]
    preview_fr.short_description = "Français"

    def preview_en(self, obj):
        return (obj.values or {}).get("en", "—")[:60]
    preview_en.short_description = "Anglais"
