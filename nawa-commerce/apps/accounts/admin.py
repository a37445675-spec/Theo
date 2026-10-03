from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Address, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "is_business_account", "loyalty_points", "is_active", "is_staff")
    list_filter = ("is_business_account", "is_active", "is_staff", "groups")
    search_fields = ("username", "email", "company_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profil NAWA", {"fields": ("phone", "avatar", "loyalty_points", "preferred_currency", "preferred_language")}),
        ("B2B", {"fields": ("is_business_account", "company_name", "vat_number")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "address_type", "city", "country", "is_default")
    list_filter = ("address_type", "country", "is_default")
    search_fields = ("full_name", "city", "user__username")
