from django.contrib import admin

from .models import DynamicTag, GlobalDesignSystem, MediaAsset, PageBlock, PageTemplate, SiteKit


class PageBlockInline(admin.TabularInline):
    model = PageBlock
    extra = 1
    fields = ("order", "block_type", "config", "dynamic_content", "is_visible")


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "is_active", "priority")
    list_filter = ("template_type", "is_active")
    search_fields = ("name",)
    inlines = [PageBlockInline]


@admin.register(GlobalDesignSystem)
class GlobalDesignSystemAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(DynamicTag)
class DynamicTagAdmin(admin.ModelAdmin):
    list_display = ("source", "label", "context")
    list_filter = ("context",)
    search_fields = ("source", "label")


@admin.register(SiteKit)
class SiteKitAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("templates",)
    actions = ["apply_kit"]

    @admin.action(description="Appliquer le kit sélectionné")
    def apply_kit(self, request, queryset):
        for kit in queryset:
            kit.apply()


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "file")
    search_fields = ("title",)


# === Widget Builder (import automatique) ===
from . import widget_admin  # noqa: F401,E402
