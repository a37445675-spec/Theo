import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class OrderStatus(models.TextChoices):
    PENDING = "pending", "En attente de paiement"
    PAID = "paid", "Payée"
    PROCESSING = "processing", "En préparation"
    SHIPPED = "shipped", "Expédiée"
    DELIVERED = "delivered", "Livrée"
    CANCELLED = "cancelled", "Annulée"
    REFUNDED = "refunded", "Remboursée"


class SalesChannel(models.TextChoices):
    ONLINE = "online", "Boutique en ligne"
    POS = "pos", "Point de vente physique"
    MARKETPLACE = "marketplace", "Marketplace tierce"


class Order(TimeStampedModel):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    guest_email = models.EmailField(blank=True)

    status = models.CharField(max_length=12, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)
    sales_channel = models.CharField(max_length=12, choices=SalesChannel.choices, default=SalesChannel.ONLINE)

    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)

    currency = models.CharField(max_length=3, default="EUR")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    coupon_code = models.CharField(max_length=32, blank=True)
    loyalty_points_earned = models.PositiveIntegerField(default=0)

    deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"NAWA-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def recompute_totals(self):
        self.subtotal = sum((item.line_total for item in self.items.all()), Decimal("0"))
        self.total = self.subtotal - self.discount_total + self.shipping_total + self.tax_total
        self.balance_due = self.total - self.deposit_paid
        self.save(update_fields=["subtotal", "total", "balance_due"])

    def add_status_history(self, status, note=""):
        self.status = status
        self.save(update_fields=["status"])
        OrderStatusHistory.objects.create(order=self, status=status, note=note)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="order_items")
    variant = models.ForeignKey("catalog.ProductVariant", null=True, blank=True, on_delete=models.PROTECT, related_name="order_items")
    product_name_snapshot = models.CharField(max_length=255)
    sku_snapshot = models.CharField(max_length=64)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product_name_snapshot}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class OrderStatusHistory(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=12, choices=OrderStatus.choices)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
