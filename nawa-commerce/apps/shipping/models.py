from django.db import models

from apps.core.mixins import TimeStampedModel


class ShippingZone(TimeStampedModel):
    name = models.CharField(max_length=100)
    countries = models.JSONField(default=list)

    def __str__(self):
        return self.name


class ShippingMethod(TimeStampedModel):
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name="methods")
    name = models.CharField(max_length=100)
    carrier = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_days_min = models.PositiveSmallIntegerField(default=3)
    estimated_days_max = models.PositiveSmallIntegerField(default=7)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.carrier})"


class ShippingLabel(TimeStampedModel):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="shipping_label")
    carrier = models.CharField(max_length=50)
    tracking_number = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(blank=True)
    pdf_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.carrier} — {self.tracking_number or 'sans suivi'}"
