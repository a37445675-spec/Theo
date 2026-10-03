"""Serializers DRF pour les scripts tiers."""
from rest_framework import serializers
from .models import ThirdPartyScript


class ThirdPartyScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyScript
        fields = ["id", "name", "code", "location", "is_active", "require_consent"]
