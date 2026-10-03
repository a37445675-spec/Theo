from django.contrib import admin

from .models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "message", "status_code", "duration_ms", "created_at")
    list_filter = ("event_type",)
    search_fields = ("message",)
    readonly_fields = ("metadata",)
