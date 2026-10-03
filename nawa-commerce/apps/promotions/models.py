from decimal import Decimal

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import TimeStampedModel


class DiscountType(models.TextChoices):
    PERCENT = "percent", "Pourcentage"
    FIXED_AMOUNT = "fixed_amount", "Montant fixe"
    FREE_SHIPPING = "free_shipping", "Livraison offerte"


class Coupon(TimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    discount_type = models.CharField(max_length=15, choices=DiscountType.choices, default=DiscountType.PERCENT)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0"), validators=[MaxValueValidator(100000)])
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicable_categories = models.ManyToManyField("catalog.Category", blank=True, related_name="coupons")

    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_customer = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self, subtotal=None) -> bool:
        now = timezone.now()
        if not self.active:
            return False
        if now < self.valid_from or (self.valid_to and now > self.valid_to):
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        if self.min_spend and subtotal is not None and subtotal < self.min_spend:
            return False
        return True

    def compute_discount(self, subtotal: Decimal) -> Decimal:
        if self.discount_type == DiscountType.PERCENT:
            return (subtotal * self.discount_value / 100).quantize(Decimal("0.01"))
        if self.discount_type == DiscountType.FIXED_AMOUNT:
            return min(self.discount_value, subtotal)
        return Decimal("0")


class VolumeDiscountRule(TimeStampedModel):
    category = models.ForeignKey("catalog.Category", null=True, blank=True, on_delete=models.CASCADE, related_name="volume_rules")
    min_quantity = models.PositiveIntegerField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["min_quantity"]

    def __str__(self):
        return f"{self.min_quantity}+ unités → -{self.discount_percent}%"
