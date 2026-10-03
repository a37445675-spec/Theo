"""Serializers DRF pour la navigation."""
from rest_framework import serializers
from .models import Menu, MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = [
            "id", "label", "url", "icon", "icon_url", "target",
            "order", "is_visible", "badge_text", "badge_color",
            "children",
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None

    def get_children(self, obj):
        children = obj.children.filter(is_visible=True).order_by("order")
        return MenuItemSerializer(children, many=True, context=self.context).data


class MenuSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["id", "name", "slug", "location", "is_active", "order", "items"]

    def get_items(self, obj):
        # On ne prend que les items racine (parent=None)
        root_items = obj.items.filter(parent=None, is_visible=True).order_by("order")
        return MenuItemSerializer(root_items, many=True, context=self.context).data
