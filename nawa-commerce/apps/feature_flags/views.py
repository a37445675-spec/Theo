"""Vues API pour les Feature Flags."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import FeatureFlag
from .serializers import FeatureFlagSerializer


class FeatureFlagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/feature-flags/  → tous les flags
    GET /api/v1/feature-flags/{id}/ → un flag
    """
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [AllowAny]
    pagination_class = None  # Pas de pagination pour les flags
