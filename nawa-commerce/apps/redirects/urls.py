"""URLs pour les redirections."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RedirectViewSet

router = DefaultRouter()
router.register(r"", RedirectViewSet, basename="redirect")

urlpatterns = [
    path("", include(router.urls)),
]
