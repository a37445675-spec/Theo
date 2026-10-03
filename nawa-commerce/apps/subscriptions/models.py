from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import TimeStampedModel


class Subscription(TimeStampedModel):
    FREQUENCY_CHOICES = [(30, "Tous les 30 jours"), (45, "Tous les 45 jours"), (60, "Tous les 60 jours"), (90, "Tous les 90 jours")]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="subscriptions")
    frequency_days = models.PositiveSmallIntegerField(choices=FREQUENCY_CHOICES, default=30)
    discount_percent = models.PositiveSmallIntegerField(default=20)
    active = models.BooleanField(default=True)
    next_delivery_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ["customer", "product"]

    def __str__(self):
        return f"Abonnement {self.customer} — {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.next_delivery_date:
            self.next_delivery_date = (timezone.now() + timezone.timedelta(days=self.frequency_days)).date()
        super().save(*args, **kwargs)

    def advance_next_delivery(self):
        self.next_delivery_date = (timezone.now() + timezone.timedelta(days=self.frequency_days)).date()
        self.save(update_fields=["next_delivery_date"])
