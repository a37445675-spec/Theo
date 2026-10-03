from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsShopManagerOrAdmin
from apps.orders.models import SalesChannel
from apps.orders.serializers import OrderSerializer
from apps.orders.services import create_order_workflow


class POSSaleLineSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)


class POSSaleSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    lines = POSSaleLineSerializer(many=True)


class POSSaleView(APIView):
    """POST /api/pos/sales/ — vente en magasin ; décrémente le stock en temps réel et alimente l'historique unifié (sales_channel=pos)."""

    permission_classes = [IsShopManagerOrAdmin]

    def post(self, request):
        from apps.accounts.models import User
        from apps.cart.models import Cart, CartLine
        from apps.catalog.models import Product, ProductVariant

        serializer = POSSaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer = User.objects.filter(pk=data["customer_id"]).first() if data.get("customer_id") else None

        cart = Cart.objects.create(customer=customer)
        for line in data["lines"]:
            product = Product.objects.get(pk=line["product_id"])
            variant = ProductVariant.objects.filter(pk=line.get("variant_id")).first() if line.get("variant_id") else None
            CartLine.objects.create(cart=cart, product=product, variant=variant, quantity=line["quantity"], unit_price=variant.effective_price if variant else product.price)

        order = create_order_workflow(cart=cart, shipping_address={}, customer=customer, sales_channel=SalesChannel.POS)
        order.add_status_history("paid", note="Vente en magasin réglée à la caisse.")
        return Response(OrderSerializer(order).data, status=201)
