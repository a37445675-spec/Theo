import logging

logger = logging.getLogger("nawa.events")


def log_event(event_type: str, message: str, user=None, metadata=None, duration_ms=None, status_code=None):
    from .models import EventLog

    logger.info("[%s] %s", event_type, message, extra={"metadata": metadata or {}})
    EventLog.objects.create(event_type=event_type, message=message, user=user, metadata=metadata or {}, duration_ms=duration_ms, status_code=status_code)
