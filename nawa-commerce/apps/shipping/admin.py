from django.contrib import admin

from .models import ShippingLabel, ShippingMethod, ShippingZone


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "carrier", "price", "is_active")
    list_filter = ("zone", "carrier", "is_active")


@admin.register(ShippingLabel)
class ShippingLabelAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "tracking_number")
