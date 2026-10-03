import logging

logger = logging.getLogger("nawa.integration")


def sync_customer_to_crm(connector, customer):
    from .models import SyncLog

    logger.info("Synchro CRM simulée — client #%s vers %s", customer.id, connector.name)
    SyncLog.objects.create(connector=connector, resource="customer", resource_id=str(customer.id), success=True, detail="Simulation")


def sync_order_to_erp(connector, order):
    from .models import SyncLog

    logger.info("Synchro ERP simulée — commande %s vers %s", order.order_number, connector.name)
    SyncLog.objects.create(connector=connector, resource="order", resource_id=order.order_number, success=True, detail="Simulation")
