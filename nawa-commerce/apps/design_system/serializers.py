"""Serializers DRF pour le Design System."""
from rest_framework import serializers
from .models import DesignSystem


class DesignSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystem
        fields = "__all__"
