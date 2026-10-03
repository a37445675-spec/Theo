"""Vues API pour le Design System."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import DesignSystem
from .serializers import DesignSystemSerializer


class DesignSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint en lecture seule pour le Design System."""
    queryset = DesignSystem.objects.all()
    serializer_class = DesignSystemSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def active(self, request):
        obj = DesignSystem.get_active()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)
