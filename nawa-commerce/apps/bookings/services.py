from apps.core.exceptions import DomainError

from .models import Booking, ServiceSlot


def book_slot(slot: ServiceSlot, customer) -> Booking:
    if not slot.is_available:
        raise DomainError("Ce créneau est complet.", code="slot_full")
    return Booking.objects.create(slot=slot, customer=customer, status=Booking.STATUS_CONFIRMED)
