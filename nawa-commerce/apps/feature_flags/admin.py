"""Admin Django pour les Feature Flags."""
from django.contrib import admin
from django.utils.html import format_html
from .models import FeatureFlag


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_enabled", "status_badge", "target_audience", "updated_at")
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
