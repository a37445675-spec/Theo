"""Vues API pour les scripts tiers."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import ThirdPartyScript
from .serializers import ThirdPartyScriptSerializer


class ThirdPartyScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/third-party-scripts/  → tous les scripts actifs
    """
    queryset = ThirdPartyScript.objects.filter(is_active=True)
    serializer_class = ThirdPartyScriptSerializer
    permission_classes = [AllowAny]
    pagination_class = None
