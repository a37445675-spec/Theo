"""Serializers DRF pour les redirections."""
from rest_framework import serializers
from .models import Redirect


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ["id", "old_path", "new_path", "redirect_type", "is_active", "hit_count"]
