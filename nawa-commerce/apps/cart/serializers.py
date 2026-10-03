from rest_framework import serializers

from apps.catalog.serializers import ProductListSerializer, ProductVariantSerializer

from .models import Cart, CartLine


class CartLineSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartLine
        fields = ["id", "product", "variant", "quantity", "unit_price", "line_total"]


class CartSerializer(serializers.ModelSerializer):
    lines = CartLineSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "status", "coupon_code", "currency", "lines", "subtotal", "total_items"]


class AddLineSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateLineSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)
