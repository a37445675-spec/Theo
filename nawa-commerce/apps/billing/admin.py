from django.contrib import admin

from .models import Invoice, InvoiceLine


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "status", "total", "issued_at", "due_at")
    list_filter = ("status",)
    search_fields = ("invoice_number", "order__order_number")
    inlines = [InvoiceLineInline]
