"""Modèles pour les scripts tiers (GA, FB Pixel, Crisp...)."""
from django.db import models


class ThirdPartyScript(models.Model):
    """Un script HTML/JS à injecter dynamiquement dans le site."""

    LOCATION_CHOICES = [
        ("head", "Dans le <head>"),
        ("body_start", "Début du <body>"),
        ("body_end", "Fin du <body>"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    code = models.TextField(
        verbose_name="Code",
        help_text="Code HTML/JS à injecter (balises <script> incluses)."
    )
    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, default="head"
    )
    is_active = models.BooleanField(default=True)
    require_consent = models.BooleanField(
        default=False,
        verbose_name="Nécessite consentement (RGPD)",
        help_text="Ne charger qu'après acceptation des cookies."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Script tiers"
        verbose_name_plural = "Scripts tiers"

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name} ({self.get_location_display()})"
