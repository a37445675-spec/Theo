"""Admin Django pour les Annonces."""
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
