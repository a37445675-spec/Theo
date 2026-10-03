from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet

router = DefaultRouter()
router.register("", InvoiceViewSet, basename="invoice")

app_name = "billing"

urlpatterns = [path("", include(router.urls))]
