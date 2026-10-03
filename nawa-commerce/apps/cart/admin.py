from django.contrib import admin

from .models import Cart, CartLine


class CartLineInline(admin.TabularInline):
    model = CartLine
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "session_key", "status", "total_items", "subtotal")
    list_filter = ("status",)
    inlines = [CartLineInline]
