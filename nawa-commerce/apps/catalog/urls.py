from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, CategoryAttributesView, CategoryViewSet, ProductVariantViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("products", ProductViewSet, basename="product")

app_name = "catalog"

urlpatterns = [
    path("categories/<slug:slug>/attributes/", CategoryAttributesView.as_view(), name="category-attributes"),
    path("products/<int:product_pk>/variants/", ProductVariantViewSet.as_view({"get": "list", "post": "create"}), name="product-variants-list"),
    path("products/<int:product_pk>/variants/<int:pk>/", ProductVariantViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="product-variants-detail"),
    path("", include(router.urls)),
]
