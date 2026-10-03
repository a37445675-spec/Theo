"""Serializers DRF pour les traductions."""
from rest_framework import serializers
from .models import TranslationKey


class TranslationKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationKey
        fields = ["id", "key", "values", "context", "description", "is_active"]
