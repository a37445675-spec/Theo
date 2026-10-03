from rest_framework import permissions, viewsets

from .models import ShippingMethod, ShippingZone
from .serializers import ShippingMethodSerializer


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = ShippingMethod.objects.filter(is_active=True).select_related("zone")
        country = self.request.query_params.get("country")
        if country:
            zone_ids = ShippingZone.objects.filter(countries__contains=[country]).values_list("id", flat=True)
            qs = qs.filter(zone_id__in=zone_ids)
        return qs
