from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "product", "product_name", "frequency_days", "discount_percent", "active", "next_delivery_date"]
        read_only_fields = ["discount_percent", "next_delivery_date"]

    def create(self, validated_data):
        request = self.context["request"]
        subscription, _ = Subscription.objects.update_or_create(
            customer=request.user, product=validated_data["product"],
            defaults={"frequency_days": validated_data["frequency_days"], "active": True},
        )
        return subscription
