from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from .models import Subscription


def create_renewal_order(subscription: Subscription):
    from apps.cart.models import Cart, CartLine
    from apps.orders.services import create_order_workflow

    cart = Cart.objects.create(customer=subscription.customer)
    discounted_price = subscription.product.price * (1 - Decimal(subscription.discount_percent) / 100)
    CartLine.objects.create(cart=cart, product=subscription.product, quantity=1, unit_price=discounted_price)

    default_address = subscription.customer.addresses.filter(is_default=True, address_type="shipping").first()
    shipping_address = {
        "full_name": default_address.full_name, "line1": default_address.line1, "city": default_address.city,
        "postal_code": default_address.postal_code, "country": default_address.country,
    } if default_address else {}

    order = create_order_workflow(cart=cart, shipping_address=shipping_address, customer=subscription.customer)
    subscription.advance_next_delivery()
    return order


@shared_task
def process_due_subscriptions():
    due = Subscription.objects.filter(active=True, next_delivery_date__lte=timezone.now().date())
    created = 0
    for subscription in due:
        try:
            create_renewal_order(subscription)
            created += 1
        except Exception:
            continue
    return f"{created} commande(s) de réassort créée(s)."
