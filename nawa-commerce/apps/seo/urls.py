"""URLs pour le SEO."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeoMetadataViewSet

router = DefaultRouter()
router.register(r"metadata", SeoMetadataViewSet, basename="seo-metadata")

urlpatterns = [
    path("", include(router.urls)),
]
