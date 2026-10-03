from apps.core.exceptions import DomainError

from .models import Cart, CartLine


def get_or_create_cart(request) -> Cart:
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(customer=request.user, status=Cart.STATUS_OPEN)
        return cart
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, customer=None, status=Cart.STATUS_OPEN)
    return cart


def add_line(cart: Cart, product, variant=None, quantity: int = 1) -> CartLine:
    if quantity <= 0:
        raise DomainError("La quantité doit être supérieure à zéro.", code="invalid_quantity")
    available_stock = variant.stock if variant else product.stock
    if product.track_stock and available_stock < quantity:
        raise DomainError(f"Stock insuffisant pour '{product.name}' (disponible : {available_stock}).", code="insufficient_stock")
    unit_price = variant.effective_price if variant else product.price
    line, created = CartLine.objects.get_or_create(cart=cart, product=product, variant=variant, defaults={"quantity": quantity, "unit_price": unit_price})
    if not created:
        line.quantity += quantity
        line.save(update_fields=["quantity"])
    return line


def update_line_quantity(line: CartLine, quantity: int) -> CartLine:
    if quantity <= 0:
        line.delete()
        return line
    line.quantity = quantity
    line.save(update_fields=["quantity"])
    return line


def merge_guest_cart_into_user_cart(guest_cart: Cart, user) -> Cart:
    user_cart, _ = Cart.objects.get_or_create(customer=user, status=Cart.STATUS_OPEN)
    for line in guest_cart.lines.all():
        add_line(user_cart, line.product, line.variant, line.quantity)
    guest_cart.status = Cart.STATUS_MERGED
    guest_cart.save(update_fields=["status"])
    return user_cart
