from django.contrib import admin

from .models import EmailCampaign, WebhookDelivery, WebhookSubscription


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("event", "target_url", "is_active")
    list_filter = ("event", "is_active")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("subscription", "status_code", "success", "created_at")
    list_filter = ("success",)
    readonly_fields = ("payload",)


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger_event", "provider", "is_active")
