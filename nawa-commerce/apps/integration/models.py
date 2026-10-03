from django.db import models

from apps.core.mixins import TimeStampedModel


class ConnectorType(models.TextChoices):
    CRM = "crm", "CRM"
    ERP = "erp", "ERP"
    EMAILING = "emailing", "Emailing"


class IntegrationConnector(TimeStampedModel):
    name = models.CharField(max_length=100)
    connector_type = models.CharField(max_length=10, choices=ConnectorType.choices)
    base_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_connector_type_display()})"


class SyncLog(TimeStampedModel):
    connector = models.ForeignKey(IntegrationConnector, on_delete=models.CASCADE, related_name="sync_logs")
    resource = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    success = models.BooleanField(default=True)
    detail = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
