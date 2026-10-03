from django.db import models

from apps.core.mixins import TimeStampedModel


class StoreLocation(TimeStampedModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return self.name


class Register(TimeStampedModel):
    store = models.ForeignKey(StoreLocation, on_delete=models.CASCADE, related_name="registers")
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.store.name} — {self.name}"
