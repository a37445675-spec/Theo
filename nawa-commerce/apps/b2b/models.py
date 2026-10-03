from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class CustomerGroup(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    payment_terms_days = models.PositiveSmallIntegerField(default=30)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="customer_groups")

    def __str__(self):
        return self.name


class PriceList(TimeStampedModel):
    group = models.OneToOneField(CustomerGroup, on_delete=models.CASCADE, related_name="price_list")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PriceListItem(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ["price_list", "product"]

    def __str__(self):
        return f"{self.price_list.name} — {self.product.name} : {self.price}"


class WholesaleTier(models.Model):
    group = models.ForeignKey(CustomerGroup, on_delete=models.CASCADE, related_name="tiers")
    min_quantity = models.PositiveIntegerField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["min_quantity"]

    def __str__(self):
        return f"{self.group.name} — {self.min_quantity}+ unités : -{self.discount_percent}%"
