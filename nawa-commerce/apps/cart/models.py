from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class Cart(TimeStampedModel):
    STATUS_OPEN = "open"
    STATUS_MERGED = "merged"
    STATUS_CONVERTED = "converted"
    STATUS_CHOICES = [(STATUS_OPEN, "Ouvert"), (STATUS_MERGED, "Fusionné"), (STATUS_CONVERTED, "Converti en commande")]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="carts")
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    coupon_code = models.CharField(max_length=32, blank=True)
    currency = models.CharField(max_length=3, default="EUR")

    class Meta:
        indexes = [models.Index(fields=["customer", "status"])]

    def __str__(self):
        return f"Panier #{self.pk} ({self.customer or self.session_key})"

    @property
    def subtotal(self) -> Decimal:
        return sum((line.line_total for line in self.lines.all()), Decimal("0"))

    @property
    def total_items(self) -> int:
        return sum(line.quantity for line in self.lines.all())


class CartLine(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("catalog.ProductVariant", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ["cart", "product", "variant"]

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
