from rest_framework import serializers

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "variant", "product_name_snapshot", "sku_snapshot", "unit_price", "quantity", "line_total"]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["status", "note", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "uuid", "status", "sales_channel", "currency",
            "shipping_address", "billing_address", "subtotal", "discount_total",
            "shipping_total", "tax_total", "total", "deposit_paid", "balance_due",
            "loyalty_points_earned", "items", "status_history", "created_at",
        ]
        read_only_fields = fields
