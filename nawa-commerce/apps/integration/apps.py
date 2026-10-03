from django.apps import AppConfig


class IntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.integration"
    label = "integration"
    verbose_name = "Intégrations CRM/ERP"
