"""Admin Django pour le Design System."""
from django.contrib import admin
from django.utils.html import format_html
from .models import DesignSystem


@admin.register(DesignSystem)
class DesignSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "color_preview", "is_active", "updated_at")
    list_filter = ("is_active",)
    readonly_fields = ("updated_at",)

    fieldsets = (
        ("Informations générales", {"fields": ("name", "is_active")}),
        ("Couleurs", {"fields": (
            "color_primary", "color_secondary", "color_accent",
            "color_background", "color_surface",
            "color_text", "color_text_muted",
            "color_error", "color_success",
        )}),
        ("Typographie", {"fields": (
            "font_heading", "font_body", "font_size_base",
            "font_size_h1", "font_size_h2", "font_size_h3", "line_height",
        )}),
        ("Formes", {"fields": ("border_radius", "button_radius", "card_radius")}),
        ("Ombres", {"fields": ("shadow_sm", "shadow_md", "shadow_lg")}),
        ("Avancé", {"fields": ("custom_css",), "classes": ("collapse",)}),
        ("Métadonnées", {"fields": ("updated_at",)}),
    )

    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:50%;vertical-align:middle;"></span> '
            '<span style="display:inline-block;width:20px;height:20px;'
            'background:{};border-radius:50%;vertical-align:middle;margin-left:4px;"></span>',
            obj.color_primary, obj.color_accent
        )
    color_preview.short_description = "Aperçu"
