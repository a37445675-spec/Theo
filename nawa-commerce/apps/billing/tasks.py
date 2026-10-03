from celery import shared_task


@shared_task
def render_invoice_pdf(invoice_id: int):
    """
    Génère le PDF de facture de façon asynchrone. Implémentation de rendu
    PDF (WeasyPrint/xhtml2pdf) à brancher : ce stub documente le contrat
    (invoice.pdf_file rempli à la fin).
    """
    from .models import Invoice

    try:
        invoice = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return
    return f"Facture {invoice.invoice_number} — génération PDF à implémenter."
