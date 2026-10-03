from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("line_total",)


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("status", "note", "created_at")


@admin.action(description="Marquer comme expédiée")
def mark_shipped(modeladmin, request, queryset):
    for order in queryset:
        order.add_status_history("shipped", note="Expédiée depuis l'admin.")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "sales_channel", "status", "total", "created_at")
    list_filter = ("status", "sales_channel", "currency")
    search_fields = ("order_number", "guest_email", "customer__username")
    readonly_fields = ("order_number", "uuid", "subtotal", "total", "balance_due", "created_at")
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    actions = [mark_shipped]
