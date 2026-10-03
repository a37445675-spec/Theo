from django.db import models

from apps.core.mixins import TimeStampedModel


class PlatformSite(TimeStampedModel):
    """Un "site" NAWA (multi-site). Base pour une future évolution multi-tenant."""

    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=255, unique=True)
    default_currency = models.CharField(max_length=3, default="EUR")
    default_language = models.CharField(max_length=5, default="fr")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.domain


class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_eur = models.DecimalField(max_digits=12, decimal_places=6, default=1)

    def __str__(self):
        return self.code


class Language(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SiteSettings(TimeStampedModel):
    site = models.OneToOneField(PlatformSite, on_delete=models.CASCADE, related_name="settings")
    tagline = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return f"Réglages — {self.site.domain}"
