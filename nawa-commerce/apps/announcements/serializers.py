"""Serializers DRF pour les Annonces."""
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id", "message", "link", "link_label",
            "background_color", "text_color",
            "icon", "icon_url",
            "position", "target_audience", "target_pages",
            "starts_at", "ends_at", "is_active", "order",
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.icon.url) if request else obj.icon.url
        return None
