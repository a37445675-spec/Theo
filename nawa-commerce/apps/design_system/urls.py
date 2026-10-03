"""URLs pour le Design System."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DesignSystemViewSet

router = DefaultRouter()
router.register(r"", DesignSystemViewSet, basename="design-system")

urlpatterns = [
    path("", include(router.urls)),
]
