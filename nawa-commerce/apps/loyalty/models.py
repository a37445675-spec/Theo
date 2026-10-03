from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class LoyaltyTransaction(TimeStampedModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loyalty_transactions")
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL, related_name="loyalty_transactions")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} — {self.points:+d} pts"
