from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsShopManagerOrAdmin

from .models import DynamicTag, GlobalDesignSystem, PageTemplate, SiteKit
from .serializers import DynamicTagSerializer, GlobalDesignSystemSerializer, PageTemplateSerializer, SiteKitSerializer


class PageTemplateViewSet(viewsets.ModelViewSet):
    """GET /api/cms/templates/?context=single_product&category=electromenager — résout le meilleur gabarit pour le contexte."""

    queryset = PageTemplate.objects.filter(is_active=True).prefetch_related("blocks")
    serializer_class = PageTemplateSerializer
    lookup_field = "slug"
    permission_classes = [IsShopManagerOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        template_type = self.request.query_params.get("context")
        if template_type:
            qs = qs.filter(template_type=template_type)
        return qs

    def list(self, request, *args, **kwargs):
        context = {k: v for k, v in request.query_params.items() if k != "context"}
        candidates = list(self.get_queryset())
        matching = [t for t in candidates if t.matches_context(context)]
        best = matching[0] if matching else (candidates[0] if candidates else None)
        if not best:
            return Response(None)
        return Response(PageTemplateSerializer(best).data)


class DesignSystemView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        design_system = GlobalDesignSystem.objects.filter(is_active=True).first()
        if not design_system:
            return Response({})
        return Response(GlobalDesignSystemSerializer(design_system).data)


class DynamicTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DynamicTag.objects.all()
    serializer_class = DynamicTagSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["context"]


class SiteKitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteKit.objects.prefetch_related("templates__blocks")
    serializer_class = SiteKitSerializer
    permission_classes = [IsShopManagerOrAdmin]


class SiteKitApplyView(APIView):
    permission_classes = [IsShopManagerOrAdmin]

    def post(self, request, pk):
        from django.shortcuts import get_object_or_404

        kit = get_object_or_404(SiteKit, pk=pk)
        kit.apply()
        return Response({"detail": f"Kit '{kit.name}' appliqué.", "templates_activated": kit.templates.count()})
