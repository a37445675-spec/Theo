from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("customer", "product", "frequency_days", "discount_percent", "active", "next_delivery_date")
    list_filter = ("active", "frequency_days")
