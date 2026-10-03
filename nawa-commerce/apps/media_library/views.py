"""Vues API pour la médiathèque."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Q
from .models import MediaAsset, MediaTag
from .serializers import MediaAssetSerializer, MediaTagSerializer


class MediaTagViewSet(viewsets.ModelViewSet):
    """CRUD complet sur les étiquettes."""
    queryset = MediaTag.objects.all()
    serializer_class = MediaTagSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class MediaAssetViewSet(viewsets.ModelViewSet):
    """
    API Médiathèque.

    GET    /api/v1/media-library/assets/                   → liste paginée
    GET    /api/v1/media-library/assets/?file_type=image   → filtré par type
    GET    /api/v1/media-library/assets/?tag=produits      → filtré par tag
    GET    /api/v1/media-library/assets/?search=karité     → recherche nom + alt
    POST   /api/v1/media-library/assets/                   → upload (multipart)
    PATCH  /api/v1/media-library/assets/{id}/              → modifier les métadonnées
    DELETE /api/v1/media-library/assets/{id}/              → supprimer
    POST   /api/v1/media-library/assets/bulk-delete/       → supprimer plusieurs
    GET    /api/v1/media-library/assets/stats/             → statistiques
    """
    queryset = MediaAsset.objects.all().prefetch_related("tags")
    serializer_class = MediaAssetSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        file_type = self.request.query_params.get("file_type")
        if file_type:
            qs = qs.filter(file_type=file_type)

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(alt_text__icontains=search) |
                Q(caption__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(uploaded_by=user)

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        """Supprime plusieurs médias d'un coup. Body : {"ids": [1, 2, 3]}"""
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "Aucun ID fourni."},
                status=status.HTTP_400_BAD_REQUEST
            )
        deleted_count = MediaAsset.objects.filter(id__in=ids).delete()[0]
        return Response({"deleted": deleted_count})

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Statistiques globales sur la médiathèque."""
        from django.db.models import Sum, Count
        total = MediaAsset.objects.count()
        by_type = list(
            MediaAsset.objects.values("file_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        total_size = MediaAsset.objects.aggregate(total=Sum("file_size"))["total"] or 0

        return Response({
            "total": total,
            "by_type": by_type,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        })
