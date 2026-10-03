"""Configuration de l'application Scripts tiers."""
from django.apps import AppConfig


class ThirdPartyScriptsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.third_party_scripts"
    verbose_name = "Scripts tiers"
