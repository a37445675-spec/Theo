"""URLs pour les traductions."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TranslationKeyViewSet

router = DefaultRouter()
router.register(r"", TranslationKeyViewSet, basename="translation")

urlpatterns = [
    path("", include(router.urls)),
]
