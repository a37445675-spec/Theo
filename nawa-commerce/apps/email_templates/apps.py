"""Configuration de l'application Templates d'emails."""
from django.apps import AppConfig


class EmailTemplatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.email_templates"
    verbose_name = "Templates d'emails"
