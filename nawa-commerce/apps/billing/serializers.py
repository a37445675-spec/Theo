from rest_framework import serializers

from .models import Invoice, InvoiceLine


class InvoiceLineSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceLine
        fields = ["description", "quantity", "unit_price", "line_total"]


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "order", "status", "issued_at", "due_at", "subtotal", "tax_total", "total", "pdf_file", "lines"]
        read_only_fields = fields
