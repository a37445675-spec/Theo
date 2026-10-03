from django.db import transaction

from apps.core.exceptions import DomainError

from .models import Order, OrderItem, OrderStatus, SalesChannel


@transaction.atomic
def create_order_workflow(cart, shipping_address, billing_address=None, customer=None, guest_email="",
                           sales_channel=SalesChannel.ONLINE, coupon=None) -> Order:
    """
    Workflow de création de commande à partir d'un panier : valide le
    stock, crée la commande + snapshot des lignes, décrémente le stock,
    applique les remises et la taxe, marque le panier comme converti.
    Appelé par apps.checkout (en ligne) et apps.pos (vente magasin).
    """
    if not cart.lines.exists():
        raise DomainError("Le panier est vide.", code="empty_cart")

    for line in cart.lines.select_related("product", "variant"):
        available = line.variant.stock if line.variant else line.product.stock
        if line.product.track_stock and available < line.quantity:
            raise DomainError(f"Stock insuffisant pour '{line.product.name}'.", code="insufficient_stock")

    order = Order.objects.create(
        customer=customer, guest_email=guest_email, shipping_address=shipping_address,
        billing_address=billing_address or shipping_address, currency=cart.currency,
        sales_channel=sales_channel, coupon_code=cart.coupon_code,
    )

    for line in cart.lines.select_related("product", "variant"):
        OrderItem.objects.create(
            order=order, product=line.product, variant=line.variant,
            product_name_snapshot=line.product.name,
            sku_snapshot=line.variant.sku if line.variant else line.product.sku,
            unit_price=line.unit_price, quantity=line.quantity,
        )
        _decrement_stock(line.product, line.variant, line.quantity)

    if coupon:
        from apps.promotions.services import apply_discounts_to_cart

        apply_discounts_to_cart(order, coupon)

    from apps.core.tax import calculate_tax

    order.recompute_totals()
    order.tax_total = calculate_tax(order)
    order.recompute_totals()
    order.add_status_history(OrderStatus.PENDING, note="Commande créée à partir du panier.")

    cart.status = "converted"
    cart.save(update_fields=["status"])

    return order


def _decrement_stock(product, variant, quantity):
    if not product.track_stock:
        return
    if variant:
        variant.stock = max(0, variant.stock - quantity)
        variant.save(update_fields=["stock"])
    else:
        product.stock = max(0, product.stock - quantity)
        product.save(update_fields=["stock"])


def mark_order_paid(order: Order):
    order.add_status_history(OrderStatus.PAID, note="Paiement confirmé.")

    from apps.loyalty.services import apply_points

    if order.customer_id:
        apply_points(order.customer, order)

    from apps.billing.services import generate_invoice_for_order

    generate_invoice_for_order(order)

    from apps.marketing.services import dispatch_webhook

    dispatch_webhook("order.paid", {"order_number": order.order_number, "total": str(order.total)})
