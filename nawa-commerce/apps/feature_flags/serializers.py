"""Serializers DRF pour les Feature Flags."""
from rest_framework import serializers
from .models import FeatureFlag


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = [
            "id", "code", "name", "description",
            "is_enabled", "target_audience",
        ]
