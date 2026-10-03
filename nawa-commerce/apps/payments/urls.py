from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet, StripeWebhookView

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payment")

app_name = "payments"

urlpatterns = [
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("", include(router.urls)),
]
