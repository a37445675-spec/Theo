from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookSlotView, ServiceSlotViewSet

router = DefaultRouter()
router.register("slots", ServiceSlotViewSet, basename="service-slot")

app_name = "bookings"

urlpatterns = [
    path("slots/<int:slot_id>/book/", BookSlotView.as_view(), name="book-slot"),
    path("", include(router.urls)),
]
