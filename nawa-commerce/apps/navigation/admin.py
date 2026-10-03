"""Admin Django pour la navigation."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Menu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    fk_name = "menu"
    extra = 1
    fields = ("order", "label", "url", "icon", "parent", "visibility", "badge_text", "is_visible")
    ordering = ("order",)
    classes = ("collapse",)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "order", "item_count", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MenuItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Éléments"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("label", "menu", "parent", "order", "visibility_badge", "badge_preview", "is_visible")
    list_filter = ("menu", "visibility", "is_visible")
    search_fields = ("label", "url")
    list_editable = ("order", "is_visible")
    ordering = ("menu", "order")

    def visibility_badge(self, obj):
        colors = {
            "all": "#6B6259",
            "anonymous": "#D4A843",
            "authenticated": "#16A34A",
            "staff": "#2F4A3C",
            "superuser": "#DC2626",
        }
        color = colors.get(obj.visibility, "#6B6259")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_visibility_display()
        )
    visibility_badge.short_description = "Visibilité"

    def badge_preview(self, obj):
        if obj.badge_text:
            return format_html(
                '<span style="background:{};color:#fff;padding:2px 8px;'
                'border-radius:999px;font-size:11px;">{}</span>',
                obj.badge_color, obj.badge_text
            )
        return "—"
    badge_preview.short_description = "Badge"
