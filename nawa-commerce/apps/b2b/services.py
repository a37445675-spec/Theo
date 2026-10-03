from decimal import Decimal


def get_price_for_customer(product, customer, quantity: int = 1) -> Decimal:
    """Résout le prix effectif : PriceList du groupe B2B si défini, sinon prix catalogue, puis palier WholesaleTier."""
    price = product.price
    group = customer.customer_groups.first() if customer and customer.is_authenticated else None
    if group:
        price_list_item = group.price_list.items.filter(product=product).first() if hasattr(group, "price_list") else None
        if price_list_item:
            price = price_list_item.price
        tier = group.tiers.filter(min_quantity__lte=quantity).order_by("-min_quantity").first()
        if tier:
            price = price * (1 - tier.discount_percent / 100)
    return price
