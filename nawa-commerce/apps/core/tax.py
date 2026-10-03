from decimal import Decimal

DEFAULT_TAX_RULES = {
    "FR": Decimal("0.20"), "BE": Decimal("0.21"), "CH": Decimal("0.081"),
    "CA": Decimal("0.05"), "CI": Decimal("0.18"), "SN": Decimal("0.18"),
}


def calculate_tax(order) -> Decimal:
    """
    Calcule la taxe applicable à une commande selon le pays de livraison.
    Point d'extension unique pour la logique fiscale (Avalara/TaxJar,
    taux réduits par catégorie, exonérations B2B...).
    """
    country = (order.shipping_address or {}).get("country", "FR")
    rate = DEFAULT_TAX_RULES.get(country, Decimal("0.20"))
    taxable_base = order.subtotal - order.discount_total
    return (taxable_base * rate).quantize(Decimal("0.01"))
