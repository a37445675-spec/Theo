"""URLs pour le Widget Builder."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .widget_views import WidgetViewSet, ReusableSectionViewSet, public_page_widgets

router = DefaultRouter()
router.register(r"widgets", WidgetViewSet, basename="widget")
router.register(r"reusable-sections", ReusableSectionViewSet, basename="reusable-section")

urlpatterns = [
    # Endpoint public (sans auth) — AVANT les routes du router
    path("pages/<int:page_id>/public/", public_page_widgets, name="public-page-widgets"),
    path("", include(router.urls)),
]
