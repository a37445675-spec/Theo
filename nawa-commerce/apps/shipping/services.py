from abc import ABC, abstractmethod
from decimal import Decimal


class CarrierGateway(ABC):
    """Interface commune à tous les transporteurs — point d'extension pour brancher de vrais SDK (DHL, Colissimo...)."""

    carrier_name: str

    @abstractmethod
    def get_live_rate(self, weight_kg: Decimal, destination_country: str) -> Decimal: ...

    @abstractmethod
    def create_label(self, order) -> dict: ...


class DHLGateway(CarrierGateway):
    carrier_name = "DHL"

    def get_live_rate(self, weight_kg, destination_country):
        return Decimal("12.90") + (weight_kg * Decimal("2.5"))

    def create_label(self, order):
        return {"tracking_number": f"DHL{order.order_number}", "tracking_url": f"https://www.dhl.com/track?id=DHL{order.order_number}", "pdf_url": ""}


class ColissimoGateway(CarrierGateway):
    carrier_name = "Colissimo"

    def get_live_rate(self, weight_kg, destination_country):
        base = Decimal("6.90") if destination_country == "FR" else Decimal("14.90")
        return base + (weight_kg * Decimal("1.2"))

    def create_label(self, order):
        return {"tracking_number": f"COL{order.order_number}", "tracking_url": f"https://www.laposte.fr/outils/suivre-vos-envois?code=COL{order.order_number}", "pdf_url": ""}


CARRIER_REGISTRY = {"dhl": DHLGateway(), "colissimo": ColissimoGateway()}


def get_gateway(carrier_code: str) -> CarrierGateway:
    return CARRIER_REGISTRY[carrier_code]


def generate_shipping_label(order, carrier_code: str):
    from .models import ShippingLabel

    gateway = get_gateway(carrier_code)
    result = gateway.create_label(order)
    label, _ = ShippingLabel.objects.update_or_create(order=order, defaults={"carrier": gateway.carrier_name, **result})
    return label
