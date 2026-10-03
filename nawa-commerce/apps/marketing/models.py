from django.db import models

from apps.core.mixins import TimeStampedModel


class WebhookSubscription(TimeStampedModel):
    event = models.CharField(max_length=100, db_index=True)
    target_url = models.URLField()
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.event} → {self.target_url}"


class WebhookDelivery(TimeStampedModel):
    subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name="deliveries")
    payload = models.JSONField()
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    success = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class EmailCampaign(TimeStampedModel):
    name = models.CharField(max_length=150)
    trigger_event = models.CharField(max_length=100)
    provider = models.CharField(max_length=30, default="sendinblue")
    template_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
