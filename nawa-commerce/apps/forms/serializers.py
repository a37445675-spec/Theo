"""Serializers DRF pour les formulaires."""
from rest_framework import serializers
from .models import FormDefinition, FormField, FormSubmission


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = [
            "id", "label", "field_key", "field_type",
            "placeholder", "help_text", "is_required",
            "default_value", "options", "order",
        ]


class FormDefinitionSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = FormDefinition
        fields = [
            "id", "name", "slug", "description",
            "success_message", "redirect_url",
            "captcha_enabled", "is_active",
            "fields",
        ]


class FormSubmissionSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source="form.name", read_only=True)

    class Meta:
        model = FormSubmission
        fields = [
            "id", "form", "form_name", "data", "status",
            "ip_address", "user_agent", "referer",
            "created_at",
        ]
        read_only_fields = [
            "ip_address", "user_agent", "referer",
            "created_at", "status",
        ]


class FormSubmitSerializer(serializers.Serializer):
    """Serializer pour la soumission publique d'un formulaire."""
    data = serializers.JSONField()
