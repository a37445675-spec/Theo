"""Serializers DRF pour le Widget Builder."""
from rest_framework import serializers
from .models import Widget, ReusableSection


class WidgetSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Widget
        fields = [
            "id", "page", "parent", "widget_type", "name",
            "content", "style",
            "custom_css", "custom_id", "custom_classes", "animation",
            "order", "is_visible", "is_locked",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.order_by("order")
        return WidgetSerializer(children, many=True).data


class ReusableSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReusableSection
        fields = "__all__"
