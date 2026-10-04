from rest_framework import serializers

from .models import (
    AttributeDefinition, AttributeSet, AttributeSetItem, Brand, Category,
    Product, ProductImage, ProductVariant,
)
from .validators import validate_attributes_against_set


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeDefinition
        fields = ["id", "code", "label", "attribute_type", "unit", "choices", "help_text", "is_filterable"]


class AttributeSetItemSerializer(serializers.ModelSerializer):
    attribute = AttributeDefinitionSerializer(read_only=True)

    class Meta:
        model = AttributeSetItem
        fields = ["attribute", "is_required", "sort_order"]


class AttributeSetSerializer(serializers.ModelSerializer):
    items = AttributeSetItemSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeSet
        fields = ["id", "name", "description", "items"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "logo", "country", "story", "website"]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "icon", "description", "children"]

    def get_children(self, obj):
        return CategorySerializer(obj.children.filter(is_active=True), many=True).data


class CategoryAttributesSerializer(serializers.ModelSerializer):
    attribute_set = AttributeSetSerializer(source="get_effective_attribute_set", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "attribute_set"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "width", "height", "order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "attributes", "price_override", "effective_price", "stock", "is_active", "images"]

    def validate(self, attrs):
        product = attrs.get("product") or getattr(self.instance, "product", None)
        attribute_set = product.category.get_effective_attribute_set() if product else None
        try:
            validate_attributes_against_set(attrs.get("attributes", {}), attribute_set, enforce_required=False)
        except Exception as exc:
            raise serializers.ValidationError({"attributes": str(exc)})
        return attrs


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "slug", "category", "brand", "product_type",
            "price", "compare_at_price", "currency", "in_stock", "is_featured",
            "cover_image", "rating_average", "reviews_count", "attributes",
        ]

    def get_cover_image(self, obj):
        first = obj.images.first()
        if not first:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(first.image.url) if request else first.image.url


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "slug", "category", "brand", "product_type", "status",
            "short_description", "description", "price", "compare_at_price", "currency",
            "stock", "track_stock", "in_stock", "attributes", "weight_kg",
            "length_cm", "width_cm", "height_cm", "is_featured",
            "rating_average", "reviews_count", "images", "variants",
            "meta_title", "meta_description", "canonical_url", "noindex",
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "sku", "name", "category", "brand", "product_type", "status",
            "short_description", "description", "price", "compare_at_price", "currency",
            "stock", "track_stock", "attributes", "weight_kg",
            "length_cm", "width_cm", "height_cm", "is_featured", "vendor",
            "meta_title", "meta_description", "canonical_url", "noindex",
        ]

    def validate(self, attrs):
        category = attrs.get("category") or getattr(self.instance, "category", None)
        attribute_set = category.get_effective_attribute_set() if category else None
        try:
            validate_attributes_against_set(attrs.get("attributes", {}) or {}, attribute_set)
        except Exception as exc:
            raise serializers.ValidationError({"attributes": str(exc)})
        return attrs


# ============================================================
#  CATEGORY ATTRIBUTES SERIALIZER
# ============================================================

class CategoryAttributeSerializer(serializers.Serializer):
    """Serializer pour les attributs dynamiques d'une catégorie."""
    code = serializers.CharField()
    label = serializers.CharField()
    attribute_type = serializers.CharField(source="attribute.attribute_type")
    unit = serializers.CharField(source="attribute.unit")
    choices = serializers.JSONField(source="attribute.choices")
    help_text = serializers.CharField(source="attribute.help_text")
    is_required = serializers.BooleanField()
    order = serializers.IntegerField(source="attribute.id")
