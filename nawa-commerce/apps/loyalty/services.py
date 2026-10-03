from django.conf import settings

from .models import LoyaltyTransaction


def apply_points(customer, order):
    points = int(order.total * settings.LOYALTY_POINTS_PER_CURRENCY_UNIT)
    if points <= 0:
        return 0
    LoyaltyTransaction.objects.create(customer=customer, points=points, reason=f"Commande {order.order_number}", order=order)
    customer.loyalty_points += points
    customer.save(update_fields=["loyalty_points"])
    return points


def redeem_points(customer, points: int, reason: str):
    from apps.core.exceptions import DomainError

    if points > customer.loyalty_points:
        raise DomainError("Solde de points insuffisant.", code="insufficient_points")
    LoyaltyTransaction.objects.create(customer=customer, points=-points, reason=reason)
    customer.loyalty_points -= points
    customer.save(update_fields=["loyalty_points"])
