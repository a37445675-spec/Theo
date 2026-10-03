from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField(required=False)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
