from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coupon


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class CouponValidateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        coupon = Coupon.objects.filter(code__iexact=data["code"]).first()
        if not coupon or not coupon.is_valid(subtotal=data["subtotal"]):
            return Response({"valid": False, "detail": "Code promo invalide ou expiré."}, status=400)

        return Response({"valid": True, "code": coupon.code, "discount_type": coupon.discount_type, "computed_discount": str(coupon.compute_discount(data["subtotal"]))})
