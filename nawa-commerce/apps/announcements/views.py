"""Vues API pour les Annonces."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/announcements/                       → toutes les annonces actives
    GET /api/v1/announcements/?position=top_bar      → filtrées par position
    GET /api/v1/announcements/?position=popup        → popup
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Announcement.objects.filter(is_active=True)
        position = self.request.query_params.get("position")
        if position:
            qs = qs.filter(position=position)
        return qs
