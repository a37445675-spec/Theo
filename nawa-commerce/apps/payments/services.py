import logging

from django.conf import settings

from .models import Payment, PaymentProvider, PaymentStatus

logger = logging.getLogger("nawa.payments")


def create_payment_intent(order, amount=None) -> dict:
    amount = amount if amount is not None else order.total
    is_deposit = amount < order.total

    payment = Payment.objects.create(order=order, provider=PaymentProvider.STRIPE, amount=amount, currency=order.currency, is_deposit=is_deposit)

    if not settings.STRIPE_SECRET_KEY:
        payment.provider_reference = f"pi_simulated_{payment.pk}"
        payment.save(update_fields=["provider_reference"])
        return {"client_secret": f"pi_simulated_{payment.pk}_secret", "payment_intent_id": payment.provider_reference, "amount": str(amount), "currency": order.currency, "simulated": True}

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.create(amount=int(amount * 100), currency=order.currency.lower(), metadata={"order_number": order.order_number, "order_id": order.id})
    payment.provider_reference = intent["id"]
    payment.save(update_fields=["provider_reference"])
    return {"client_secret": intent["client_secret"], "payment_intent_id": intent["id"], "amount": str(amount), "currency": order.currency}


def handle_stripe_webhook_event(event: dict):
    event_type = event.get("type")
    payment_intent_id = event.get("data", {}).get("object", {}).get("id")
    if not payment_intent_id:
        return

    payment = Payment.objects.filter(provider_reference=payment_intent_id).first()
    if not payment:
        logger.warning("Webhook Stripe reçu pour un paiement inconnu: %s", payment_intent_id)
        return

    if event_type == "payment_intent.succeeded":
        payment.status = PaymentStatus.SUCCEEDED
        payment.raw_response = event
        payment.save(update_fields=["status", "raw_response"])

        order = payment.order
        if payment.is_deposit:
            order.deposit_paid += payment.amount
            order.recompute_totals()
        else:
            from apps.orders.services import mark_order_paid

            mark_order_paid(order)

    elif event_type == "payment_intent.payment_failed":
        payment.status = PaymentStatus.FAILED
        payment.raw_response = event
        payment.save(update_fields=["status", "raw_response"])
