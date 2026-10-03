"""Serializers DRF pour les emails."""
from rest_framework import serializers
from .models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "id", "code", "name", "description",
            "subject", "body_text", "body_html",
            "from_email", "variables", "is_active",
        ]
