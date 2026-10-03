"""URLs pour le Widget Builder."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .widget_views import WidgetViewSet, ReusableSectionViewSet

router = DefaultRouter()
router.register(r"widgets", WidgetViewSet, basename="widget")
router.register(r"reusable-sections", ReusableSectionViewSet, basename="reusable-section")

urlpatterns = [
    path("", include(router.urls)),
]
