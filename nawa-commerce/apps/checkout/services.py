from apps.orders.models import SalesChannel
from apps.orders.services import create_order_workflow
from apps.payments.services import create_payment_intent
from apps.promotions.models import Coupon


def checkout_cart(cart, shipping_address, billing_address, customer, guest_email="", coupon_code=""):
    """
    Point d'entrée unique du tunnel de commande : résout le coupon, délègue
    la création de commande à orders.services, crée l'intention de paiement.
    """
    coupon = None
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code, active=True).first()

    order = create_order_workflow(
        cart=cart, shipping_address=shipping_address, billing_address=billing_address,
        customer=customer, guest_email=guest_email, sales_channel=SalesChannel.ONLINE, coupon=coupon,
    )
    payment_intent = create_payment_intent(order)
    return order, payment_intent
