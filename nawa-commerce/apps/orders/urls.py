from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, ShopManagerOrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")
router.register("manage", ShopManagerOrderViewSet, basename="order-manage")

app_name = "orders"

urlpatterns = [path("", include(router.urls))]
