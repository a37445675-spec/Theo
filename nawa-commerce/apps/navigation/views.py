"""Vues API pour la navigation."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Menu
from .serializers import MenuSerializer


class MenuViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/navigation/menus/              → tous les menus actifs
    GET /api/v1/navigation/menus/?location=header → filtre par emplacement
    GET /api/v1/navigation/menus/{id}/         → détail d'un menu
    GET /api/v1/navigation/menus/by-slug/{slug}/ → récupération par slug
    """
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        qs = Menu.objects.filter(is_active=True).prefetch_related("items__children")
        location = self.request.query_params.get("location")
        if location:
            qs = qs.filter(location=location)
        return qs

    @action(detail=False, methods=["get"], url_path=r"by-slug/(?P<slug>[\w-]+)")
    def by_slug(self, request, slug=None):
        menu = get_object_or_404(Menu, slug=slug, is_active=True)
        serializer = self.get_serializer(menu)
        return Response(serializer.data)
