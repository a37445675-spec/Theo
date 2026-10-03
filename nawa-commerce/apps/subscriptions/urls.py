from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscriptionViewSet

router = DefaultRouter()
router.register("", SubscriptionViewSet, basename="subscription")

app_name = "subscriptions"

urlpatterns = [path("", include(router.urls))]
