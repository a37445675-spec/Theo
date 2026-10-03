"""Serializers DRF pour le SEO."""
from rest_framework import serializers
from .models import SeoMetadata


class SeoMetadataSerializer(serializers.ModelSerializer):
    og_image_url = serializers.SerializerMethodField()
    content_object_str = serializers.SerializerMethodField()

    class Meta:
        model = SeoMetadata
        fields = [
            "id", "content_type", "object_id", "content_object_str",
            "meta_title", "meta_description", "meta_keywords",
            "og_title", "og_description", "og_image", "og_image_url", "og_type",
            "twitter_card", "canonical_url", "robots",
            "structured_data", "updated_at",
        ]

    def get_og_image_url(self, obj):
        if obj.og_image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.og_image.url) if request else obj.og_image.url
        return None

    def get_content_object_str(self, obj):
        try:
            return str(obj.content_object)
        except Exception:
            return None
