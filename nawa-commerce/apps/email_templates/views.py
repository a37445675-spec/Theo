"""Vues API pour les emails."""
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import EmailTemplate
from .serializers import EmailTemplateSerializer


class EmailTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API privée (réservée au staff).

    GET /api/v1/email-templates/
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
