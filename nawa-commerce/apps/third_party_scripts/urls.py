"""URLs pour les scripts tiers."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThirdPartyScriptViewSet

router = DefaultRouter()
router.register(r"", ThirdPartyScriptViewSet, basename="third-party-script")

urlpatterns = [
    path("", include(router.urls)),
]
