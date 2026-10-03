from rest_framework import serializers

from .models import ShippingLabel, ShippingMethod


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ["id", "name", "carrier", "price", "estimated_days_min", "estimated_days_max"]


class ShippingLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingLabel
        fields = ["carrier", "tracking_number", "tracking_url", "pdf_url"]
