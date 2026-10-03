from django.contrib import admin

from .models import Booking, ServiceSlot


@admin.register(ServiceSlot)
class ServiceSlotAdmin(admin.ModelAdmin):
    list_display = ("product", "start_at", "duration_minutes", "capacity", "booked_count")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "slot", "status")
    list_filter = ("status",)
