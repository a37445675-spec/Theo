import hashlib
import hmac
import logging

from celery import shared_task

logger = logging.getLogger("nawa.marketing")


def dispatch_webhook(event: str, payload: dict):
    from .models import WebhookSubscription

    subscription_ids = list(WebhookSubscription.objects.filter(event=event, is_active=True).values_list("id", flat=True))
    for subscription_id in subscription_ids:
        send_webhook_delivery.delay(subscription_id, payload)


@shared_task
def send_webhook_delivery(subscription_id: int, payload: dict):
    import requests

    from .models import WebhookDelivery, WebhookSubscription

    subscription = WebhookSubscription.objects.get(pk=subscription_id)
    headers = {"Content-Type": "application/json"}
    if subscription.secret:
        signature = hmac.new(subscription.secret.encode(), str(payload).encode(), hashlib.sha256).hexdigest()
        headers["X-NAWA-Signature"] = signature
    try:
        response = requests.post(subscription.target_url, json=payload, headers=headers, timeout=10)
        WebhookDelivery.objects.create(subscription=subscription, payload=payload, status_code=response.status_code, success=response.ok)
    except Exception as exc:
        logger.warning("Échec de livraison webhook %s: %s", subscription.target_url, exc)
        WebhookDelivery.objects.create(subscription=subscription, payload=payload, status_code=None, success=False)


def send_via_provider(campaign, recipient_email: str, context: dict):
    logger.info("Envoi simulé — campagne '%s' vers %s via %s", campaign.name, recipient_email, campaign.provider)
    return {"provider": campaign.provider, "recipient": recipient_email, "status": "simulated"}
