from rest_framework import permissions, viewsets

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Invoice.objects.prefetch_related("lines")
        return qs if user.is_shop_manager else qs.filter(order__customer=user)
