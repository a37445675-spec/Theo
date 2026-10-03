from django.contrib import admin

from .models import CustomerGroup, PriceList, PriceListItem, WholesaleTier


class PriceListItemInline(admin.TabularInline):
    model = PriceListItem
    extra = 1


class WholesaleTierInline(admin.TabularInline):
    model = WholesaleTier
    extra = 1


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "minimum_order_amount", "payment_terms_days")
    filter_horizontal = ("members",)
    inlines = [WholesaleTierInline]


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    inlines = [PriceListItemInline]
