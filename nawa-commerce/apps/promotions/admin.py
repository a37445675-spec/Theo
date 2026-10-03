from django.contrib import admin

from .models import Coupon, VolumeDiscountRule


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "active", "times_used", "usage_limit")
    list_filter = ("discount_type", "active")
    search_fields = ("code",)
    filter_horizontal = ("applicable_categories",)


@admin.register(VolumeDiscountRule)
class VolumeDiscountRuleAdmin(admin.ModelAdmin):
    list_display = ("category", "min_quantity", "discount_percent")
    list_filter = ("category",)
