"""Vues API pour les redirections."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Redirect
from .serializers import RedirectSerializer


class RedirectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique des redirections actives.

    GET /api/v1/redirects/
    GET /api/v1/redirects/?path=/ancienne-url  → résout une URL spécifique
    """
    serializer_class = RedirectSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Redirect.objects.filter(is_active=True)
        path = self.request.query_params.get("path")
        if path:
            qs = qs.filter(old_path=path)
        return qs
