from datetime import timedelta

from django.utils import timezone

from .models import Invoice, InvoiceLine


def generate_invoice_for_order(order) -> Invoice:
    """Génère la facture d'une commande payée ; échéance J+30 pour les comptes B2B (net 30)."""
    is_b2b = bool(order.customer_id and order.customer.is_business_account)

    invoice, created = Invoice.objects.get_or_create(
        order=order,
        defaults={
            "subtotal": order.subtotal, "tax_total": order.tax_total, "total": order.total,
            "due_at": timezone.now() + timedelta(days=30) if is_b2b else timezone.now(),
        },
    )
    if created:
        for item in order.items.all():
            InvoiceLine.objects.create(invoice=invoice, description=item.product_name_snapshot, quantity=item.quantity, unit_price=item.unit_price)
        from .tasks import render_invoice_pdf

        render_invoice_pdf.delay(invoice.id)

    return invoice
