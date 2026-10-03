"""Serializers DRF pour la médiathèque."""
from rest_framework import serializers
from .models import MediaAsset, MediaTag


class MediaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaTag
        fields = ["id", "name", "slug", "color"]


class MediaAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    tags = MediaTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=MediaTag.objects.all(),
        source="tags", required=False
    )
    file_size_human = serializers.ReadOnlyField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id", "name", "alt_text", "caption",
            "file", "file_url", "thumbnail_url",
            "file_type", "mime_type", "file_size", "file_size_human",
            "width", "height",
            "tags", "tag_ids",
            "uploaded_by", "uploaded_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "file_type", "mime_type", "file_size",
            "width", "height", "uploaded_by",
            "created_at", "updated_at",
        ]
        extra_kwargs = {
            "file": {"required": True},
            "name": {"required": False},
        }

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def get_thumbnail_url(self, obj):
        """
        Retourne une URL de miniature.
        Si l'image est < 400px, on renvoie l'original.
        Sinon, on pourrait générer une miniature à la volée (via sorl-thumbnail par ex.).
        Pour l'instant, retourne l'original.
        """
        if not obj.file or obj.file_type != "image":
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.username
        return None

    def create(self, validated_data):
        # Auto-nommer à partir du nom de fichier si non fourni
        if not validated_data.get("name"):
            validated_data["name"] = os.path.splitext(
                os.path.basename(validated_data["file"].name)
            )[0]
        return super().create(validated_data)


import os  # noqa: E402  (placé en bas pour lisibilité)
