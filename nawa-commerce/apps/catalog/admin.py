from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import (
    AttributeDefinition, AttributeSet, AttributeSetItem, Brand, Category,
    Product, ProductImage, ProductVariant,
)


class AttributeSetItemInline(admin.TabularInline):
    model = AttributeSetItem
    extra = 1
    autocomplete_fields = ["attribute"]


@admin.register(AttributeDefinition)
class AttributeDefinitionAdmin(admin.ModelAdmin):
    list_display = ("label", "code", "attribute_type", "unit", "is_filterable")
    list_filter = ("attribute_type", "is_filterable")
    search_fields = ("code", "label")
    prepopulated_fields = {"code": ("label",)}


@admin.register(AttributeSet)
class AttributeSetAdmin(admin.ModelAdmin):
    list_display = ("name", "attribute_count")
    inlines = [AttributeSetItemInline]
    search_fields = ("name",)

    def attribute_count(self, obj):
        return obj.items.count()
    attribute_count.short_description = "Nb. attributs"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "attribute_set", "is_active", "sort_order")
    list_filter = ("is_active", "attribute_set")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["parent", "attribute_set"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {"attributes": forms.Textarea(attrs={"rows": 6, "class": "vLargeTextField"})}

    def clean(self):
        cleaned_data = super().clean()
        instance = Product(category=cleaned_data.get("category"), attributes=cleaned_data.get("attributes") or {})
        try:
            instance.clean()
        except ValidationError as exc:
            raise forms.ValidationError(exc.message if hasattr(exc, "message") else str(exc))
        return cleaned_data


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:60px;border-radius:6px;" />', obj.image.url)
        return "—"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("sku", "attributes", "price_override", "stock", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "sku", "category", "brand", "product_type", "status", "price", "stock_display")
    list_filter = ("status", "product_type", "category", "brand")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category", "brand", "vendor"]
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = ("rating_average", "reviews_count")

    fieldsets = (
        (None, {"fields": ("name", "slug", "sku", "category", "brand", "vendor", "product_type", "status")}),
        ("Contenu", {"fields": ("short_description", "description")}),
        ("Prix & stock", {"fields": ("price", "compare_at_price", "currency", "stock", "track_stock")}),
        ("Attributs dynamiques", {"fields": ("attributes",)}),
        ("Logistique", {"classes": ("collapse",), "fields": ("weight_kg", "length_cm", "width_cm", "height_cm")}),
        ("SEO", {"classes": ("collapse",), "fields": ("meta_title", "meta_description", "canonical_url", "noindex")}),
        ("Avis (calculés)", {"fields": ("rating_average", "reviews_count")}),
    )

    def stock_display(self, obj):
        return "Variantes" if obj.product_type == "variant" else obj.stock
    stock_display.short_description = "Stock"
