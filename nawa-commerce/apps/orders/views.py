from rest_framework import permissions, viewsets

from apps.core.permissions import IsShopManagerOrAdmin

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "sales_channel"]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items", "status_history")
        user = self.request.user
        if user.is_shop_manager:
            return qs
        return qs.filter(customer=user)


class ShopManagerOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsShopManagerOrAdmin]
    queryset = Order.objects.prefetch_related("items", "status_history")
    filterset_fields = ["status", "sales_channel"]
