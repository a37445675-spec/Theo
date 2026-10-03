from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cart.services import get_or_create_cart
from apps.orders.serializers import OrderSerializer

from .serializers import CheckoutSerializer
from .services import checkout_cart


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = get_or_create_cart(request)
        customer = request.user if request.user.is_authenticated else None

        order, payment_intent = checkout_cart(
            cart=cart, shipping_address=data["shipping_address"], billing_address=data.get("billing_address"),
            customer=customer, guest_email=data.get("guest_email", ""), coupon_code=data.get("coupon_code", ""),
        )
        return Response({"order": OrderSerializer(order).data, "payment_intent": payment_intent}, status=201)
