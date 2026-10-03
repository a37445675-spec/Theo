"""Admin Django pour le Widget Builder."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Widget, ReusableSection


class WidgetChildInline(admin.TabularInline):
    model = Widget
    fk_name = "parent"
    extra = 0
    fields = ("order", "widget_type", "name", "is_visible")
    ordering = ("order",)
    show_change_link = True


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ("id", "type_badge", "name", "page", "parent", "order", "is_visible")
    list_filter = ("widget_type", "is_visible", "page")
    search_fields = ("name", "widget_type")
    list_editable = ("order", "is_visible")
    inlines = [WidgetChildInline]
    ordering = ("page", "order")

    fieldsets = (
        ("Identification", {"fields": ("page", "parent", "widget_type", "name")}),
        ("Contenu (JSON)", {"fields": ("content",), "classes": ("collapse",)}),
        ("Style (JSON)", {"fields": ("style",), "classes": ("collapse",)}),
        ("Avancé", {
            "fields": ("custom_css", "custom_id", "custom_classes", "animation"),
            "classes": ("collapse",)
        }),
        ("Ordre & Visibilité", {"fields": ("order", "is_visible", "is_locked")}),
    )

    def type_badge(self, obj):
        colors = {
            "section": "#C1652F", "column": "#8A4B26",
            "heading": "#2F4A3C", "text": "#6B6259",
            "image": "#D4A843", "button": "#16A34A",
            "product_grid": "#DC2626", "carousel": "#1E40AF",
        }
        color = colors.get(obj.widget_type, "#221B15")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_widget_type_display()
        )
    type_badge.short_description = "Type"


@admin.register(ReusableSection)
class ReusableSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
