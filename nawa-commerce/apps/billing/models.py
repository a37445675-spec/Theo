from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.mixins import TimeStampedModel


class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Brouillon"
    ISSUED = "issued", "Émise"
    PAID = "paid", "Payée"
    OVERDUE = "overdue", "En retard"
    CANCELLED = "cancelled", "Annulée"


class Invoice(TimeStampedModel):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=30, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.ISSUED)

    issued_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    pdf_file = models.FileField(upload_to="invoices/%Y/%m/", blank=True, null=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{timezone.now():%Y%m}-{self.order_id or '0'}"
        super().save(*args, **kwargs)


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    def __str__(self):
        return self.description
