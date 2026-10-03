"""URLs pour la médiathèque."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaAssetViewSet, MediaTagViewSet

router = DefaultRouter()
router.register(r"assets", MediaAssetViewSet, basename="media-asset")
router.register(r"tags", MediaTagViewSet, basename="media-tag")

urlpatterns = [
    path("", include(router.urls)),
]
