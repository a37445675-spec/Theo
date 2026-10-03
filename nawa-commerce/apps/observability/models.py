from django.conf import settings
from django.db import models

from apps.core.mixins import TimeStampedModel


class EventLog(TimeStampedModel):
    """Journal d'événements structuré (requêtes lentes, erreurs 5xx, actions métier sensibles)."""

    event_type = models.CharField(max_length=100, db_index=True)
    message = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    metadata = models.JSONField(default=dict, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["event_type", "created_at"])]

    def __str__(self):
        return f"{self.event_type} — {self.message}"
