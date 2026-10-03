from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "address_type", "full_name", "line1", "line2", "city", "postal_code", "country", "phone", "is_default"]


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    loyalty_tier = serializers.SerializerMethodField()
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "phone", "avatar",
            "is_business_account", "company_name", "vat_number",
            "loyalty_points", "loyalty_tier", "preferred_currency", "preferred_language",
            "roles", "addresses", "date_joined",
        ]
        read_only_fields = ["id", "loyalty_points", "date_joined"]

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_loyalty_tier(self, obj):
        return obj.loyalty_tier()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    is_vendor = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "is_vendor"]

    def create(self, validated_data):
        from django.contrib.auth.models import Group

        from .models import ROLE_CUSTOMER, ROLE_VENDOR

        password = validated_data.pop("password")
        wants_vendor = validated_data.pop("is_vendor", False)
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        roles = [ROLE_CUSTOMER] + ([ROLE_VENDOR] if wants_vendor else [])
        user.groups.set(Group.objects.filter(name__in=roles))
        return user
