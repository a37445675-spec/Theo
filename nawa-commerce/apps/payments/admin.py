from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "is_deposit", "created_at")
    list_filter = ("provider", "status", "is_deposit")
    search_fields = ("order__order_number", "provider_reference")
    readonly_fields = ("raw_response",)
