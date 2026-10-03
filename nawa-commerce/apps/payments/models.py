from django.db import models

from apps.core.mixins import TimeStampedModel


class PaymentProvider(models.TextChoices):
    STRIPE = "stripe", "Stripe"
    MANUAL = "manual", "Manuel"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    SUCCEEDED = "succeeded", "Réussi"
    FAILED = "failed", "Échoué"
    REFUNDED = "refunded", "Remboursé"


class Payment(TimeStampedModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=10, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE)
    provider_reference = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    is_deposit = models.BooleanField(default=False)
    raw_response = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Paiement {self.amount} {self.currency} — {self.order.order_number}"
