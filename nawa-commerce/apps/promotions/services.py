from decimal import Decimal

from apps.core.exceptions import DomainError


def apply_discounts_to_cart(order, coupon):
    """Applique un coupon à une commande en cours de création (voir orders.services.create_order_workflow)."""
    subtotal = sum((item.line_total for item in order.items.all()), Decimal("0"))

    if not coupon.is_valid(subtotal=subtotal):
        raise DomainError(f"Le code promo '{coupon.code}' n'est plus valide.", code="invalid_coupon")

    from .models import DiscountType

    if coupon.discount_type == DiscountType.FREE_SHIPPING:
        order.shipping_total = Decimal("0")
    else:
        order.discount_total = coupon.compute_discount(subtotal)

    order.coupon_code = coupon.code
    order.save(update_fields=["discount_total", "shipping_total", "coupon_code"])

    coupon.times_used += 1
    coupon.save(update_fields=["times_used"])
    return order


def get_volume_discount_percent(category, quantity: int) -> Decimal:
    from .models import VolumeDiscountRule

    rule = VolumeDiscountRule.objects.filter(category=category, min_quantity__lte=quantity).order_by("-min_quantity").first()
    return rule.discount_percent if rule else Decimal("0")
