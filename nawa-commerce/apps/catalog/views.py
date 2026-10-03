from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from apps.core.permissions import IsShopManagerOrAdmin

from .filters import DynamicAttributeFilterBackend, ProductFilter
from .models import Brand, Category, Product, ProductVariant
from .serializers import (
    BrandSerializer, CategoryAttributesSerializer, CategorySerializer,
    ProductDetailSerializer, ProductListSerializer, ProductVariantSerializer, ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Category.objects.filter(is_active=True)
        if self.action == "list":
            return qs.filter(parent__isnull=True)
        return qs


class CategoryAttributesView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryAttributesSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    permission_classes = [IsShopManagerOrAdmin]
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, DynamicAttributeFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "sku", "short_description", "description"]
    ordering_fields = ["price", "created_at", "rating_average"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductWriteSerializer

    def get_queryset(self):
        qs = Product.objects.select_related("category", "brand").prefetch_related("images", "variants")
        if not (self.request.user.is_authenticated and self.request.user.is_shop_manager):
            qs = qs.filter(status="active")
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductDetailSerializer(instance, context={"request": request})
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariantSerializer
    permission_classes = [IsShopManagerOrAdmin]

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs["product_pk"])
