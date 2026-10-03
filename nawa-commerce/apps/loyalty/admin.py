from django.contrib import admin

from .models import LoyaltyTransaction


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ("customer", "points", "reason", "created_at")
    search_fields = ("customer__username", "reason")
