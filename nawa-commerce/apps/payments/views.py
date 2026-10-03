import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, viewsets
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer
from .services import handle_stripe_webhook_event

logger = logging.getLogger("nawa.payments")


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related("order")
        return qs if user.is_shop_manager else qs.filter(order__customer=user)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        if settings.STRIPE_WEBHOOK_SECRET:
            import stripe

            try:
                event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
            except Exception as exc:
                logger.warning("Webhook Stripe rejeté : %s", exc)
                return HttpResponse(status=400)
        else:
            event = json.loads(payload or "{}")

        handle_stripe_webhook_event(event)
        return HttpResponse(status=200)
