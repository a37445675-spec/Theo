"""Configuration de l'application Design System."""
from django.apps import AppConfig


class DesignSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.design_system"
    verbose_name = "Design System"
