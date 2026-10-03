"""Admin Django pour les redirections."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "type_badge", "is_active", "hit_count", "updated_at")
    list_filter = ("redirect_type", "is_active")
    search_fields = ("old_path", "new_path")
    list_editable = ("is_active",)
    readonly_fields = ("hit_count", "created_at", "updated_at")
    ordering = ("-updated_at",)

    def type_badge(self, obj):
        color = "#16A34A" if obj.redirect_type == "301" else "#D4A843"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.redirect_type
        )
    type_badge.short_description = "Type"
