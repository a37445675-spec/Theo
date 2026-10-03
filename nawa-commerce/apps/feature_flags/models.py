"""Modèles pour les Feature Flags (interrupteurs de fonctionnalités)."""
from django.db import models


class FeatureFlag(models.Model):
    """
    Un feature flag permet d'activer/désactiver une fonctionnalité
    depuis l'admin, sans redéployer le code.

    Exemples :
      - code="wishlist"       → active la liste de souhaits
      - code="reviews"        → active les avis clients
      - code="header_search"  → affiche la barre de recherche
      - code="guest_checkout" → autorise la commande sans compte
    """

    TARGET_AUDIENCE_CHOICES = [
        ("all", "Tout le monde"),
        ("authenticated", "Utilisateurs connectés"),
        ("staff", "Staff uniquement"),
        ("beta", "Bêta-testeurs"),
    ]

    code = models.SlugField(
        max_length=100, unique=True,
        help_text="Identifiant technique (ex: wishlist, reviews)."
    )
    name = models.CharField(max_length=200, verbose_name="Nom affiché")
    description = models.TextField(
        blank=True,
        help_text="Description de ce que fait ce flag."
    )
    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Activé",
        help_text="Activer la fonctionnalité dans le frontend."
    )
    target_audience = models.CharField(
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        default="all",
        verbose_name="Audience cible",
        help_text="À qui s'applique ce flag ?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    def __str__(self):
        status = "✅" if self.is_enabled else "❌"
        return f"{status} {self.code} — {self.name}"
