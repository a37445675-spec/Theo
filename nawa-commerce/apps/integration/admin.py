from django.contrib import admin

from .models import IntegrationConnector, SyncLog


@admin.register(IntegrationConnector)
class IntegrationConnectorAdmin(admin.ModelAdmin):
    list_display = ("name", "connector_type", "is_active")
    list_filter = ("connector_type", "is_active")


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ("connector", "resource", "resource_id", "success", "created_at")
    list_filter = ("success", "resource")
