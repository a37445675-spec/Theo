from rest_framework import serializers

from .models import DynamicTag, GlobalDesignSystem, MediaAsset, PageBlock, PageTemplate, SiteKit


class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ["id", "file", "title", "alt_text"]


class PageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageBlock
        fields = ["id", "block_type", "order", "config", "dynamic_content", "is_visible"]


class PageTemplateSerializer(serializers.ModelSerializer):
    blocks = PageBlockSerializer(many=True, read_only=True)

    class Meta:
        model = PageTemplate
        fields = ["id", "name", "slug", "template_type", "display_conditions", "is_active", "priority", "blocks"]


class GlobalDesignSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalDesignSystem
        fields = '__all__'


class DynamicTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicTag
        fields = ["source", "label", "context"]


class SiteKitSerializer(serializers.ModelSerializer):
    templates = PageTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = SiteKit
        fields = ["id", "name", "slug", "description", "templates"]
