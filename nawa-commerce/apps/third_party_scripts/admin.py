"""Admin Django pour les scripts tiers."""
from django.contrib import admin
from django.utils.html import format_html
from .models import ThirdPartyScript


@admin.register(ThirdPartyScript)
class ThirdPartyScriptAdmin(admin.ModelAdmin):
    list_display = ("name", "location_badge", "consent_badge", "is_active", "updated_at")
    list_filter = ("location", "is_active", "require_consent")
    search_fields = ("name", "description")
    list_editable = ("is_active",)

    fieldsets = (
        ("Identification", {"fields": ("name", "description")}),
        ("Code à injecter", {
            "fields": ("code", "location", "is_active", "require_consent")
        }),
    )

    def location_badge(self, obj):
        colors = {"head": "#DC2626", "body_start": "#D4A843", "body_end": "#2F4A3C"}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            colors.get(obj.location, "#6B6259"),
            obj.get_location_display()
        )
    location_badge.short_description = "Emplacement"

    def consent_badge(self, obj):
        if obj.require_consent:
            return format_html(
                '<span style="color:#D4A843;font-weight:600;">⚠ RGPD</span>'
            )
        return "—"
    consent_badge.short_description = "Consentement"
