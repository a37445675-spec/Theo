from django.contrib import admin

from .models import Register, StoreLocation


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country")


@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "is_active")
