from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ShippingMethodViewSet

router = DefaultRouter()
router.register("methods", ShippingMethodViewSet, basename="shipping-method")

app_name = "shipping"

urlpatterns = [path("", include(router.urls))]
