from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class ServiceSlot(TimeStampedModel):
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="service_slots")
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    capacity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["start_at"]

    def __str__(self):
        return f"{self.product.name} — {self.start_at:%d/%m/%Y %H:%M}"

    @property
    def booked_count(self) -> int:
        return self.bookings.filter(status=Booking.STATUS_CONFIRMED).count()

    @property
    def is_available(self) -> bool:
        return self.booked_count < self.capacity


class Booking(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [(STATUS_PENDING, "En attente"), (STATUS_CONFIRMED, "Confirmée"), (STATUS_CANCELLED, "Annulée")]

    slot = models.ForeignKey(ServiceSlot, on_delete=models.CASCADE, related_name="bookings")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"{self.customer} — {self.slot}"
