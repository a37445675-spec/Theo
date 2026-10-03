"""Vues API pour le SEO."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from .models import SeoMetadata
from .serializers import SeoMetadataSerializer


class SeoMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API SEO en lecture seule.

    GET /api/v1/seo/metadata/                                → liste
    GET /api/v1/seo/metadata/?content_type=page_template&object_id=1 → détail par objet
    GET /api/v1/seo/metadata/?model=catalog.product&pk=5     → détail (API friendly)
    GET /api/v1/seo/metadata/for-url/?url=/boutique/cosmetiques → résolution par URL
    """
    queryset = SeoMetadata.objects.all()
    serializer_class = SeoMetadataSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        ct = self.request.query_params.get("content_type")
        oid = self.request.query_params.get("object_id")
        if ct and oid:
            qs = qs.filter(content_type__model=ct, object_id=oid)
        return qs

    @action(detail=False, methods=["get"])
    def for_url(self, request):
        """Résout le SEO à partir d'une URL en cherchant dans PageTemplate, Product, BlogPost."""
        url = request.query_params.get("url", "/").rstrip("/") or "/"
        result = None

        # 1. Essayer PageTemplate par slug ou route
        try:
            PageTemplate = apps.get_model("cms", "PageTemplate")
            pt = PageTemplate.objects.filter(slug=url.strip("/")).first()
            if pt:
                result = SeoMetadata.objects.filter(
                    content_type=ContentType.objects.get_for_model(PageTemplate),
                    object_id=pt.id,
                ).first()
        except LookupError:
            pass

        # 2. Essayer Product par slug
        if not result:
            try:
                Product = apps.get_model("catalog", "Product")
                product = Product.objects.filter(slug=url.strip("/").split("/")[-1]).first()
                if product:
                    result = SeoMetadata.objects.filter(
                        content_type=ContentType.objects.get_for_model(Product),
                        object_id=product.id,
                    ).first()
            except LookupError:
                pass

        # 3. Essayer BlogPost par slug
        if not result:
            try:
                Post = apps.get_model("blog", "Post")
                post = Post.objects.filter(slug=url.strip("/").split("/")[-1]).first()
                if post:
                    result = SeoMetadata.objects.filter(
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=post.id,
                    ).first()
            except LookupError:
                pass

        if not result:
            return Response({"detail": "Aucune métadonnée SEO pour cette URL."}, status=404)

        serializer = self.get_serializer(result)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sitemap(self, request):
        """Génère un sitemap JSON des URLs indexables."""
        urls = []
        try:
            Product = apps.get_model("catalog", "Product")
            for p in Product.objects.filter(status="active"):
                urls.append({"loc": f"/produit/{p.slug}", "changefreq": "weekly"})
        except LookupError:
            pass
        try:
            Post = apps.get_model("blog", "Post")
            for p in Post.objects.filter(status="published"):
                urls.append({"loc": f"/journal/{p.slug}", "changefreq": "monthly"})
        except LookupError:
            pass
        return Response({"urls": urls})
