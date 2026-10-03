"""Modèles pour les traductions (i18n pilotable depuis l'admin)."""
from django.db import models


class TranslationKey(models.Model):
    """
    Clé de traduction. Exemple : key="cart.empty.message"
    La valeur pour chaque langue est stockée dans un JSONField.
    """

    key = models.CharField(
        max_length=200, unique=True,
        help_text="Identifiant unique. Convention : module.section.cle (ex: cart.empty.message)",
    )
    values = models.JSONField(
        default=dict,
        help_text='Format : {"fr": "...", "en": "..."}',
    )
    context = models.CharField(
        max_length=100, blank=True,
        help_text="Où ce texte apparaît (ex: Panier, Header).",
    )
    description = models.TextField(
        blank=True,
        help_text="Notes pour les traducteurs (contexte, ton, variables).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]
        verbose_name = "Clé de traduction"
        verbose_name_plural = "Clés de traduction"

    def __str__(self):
        return self.key

    def get_value(self, lang="fr", fallback=True):
        """Récupère la valeur pour une langue, avec fallback sur 'fr'."""
        if not self.values:
            return self.key
        if lang in self.values and self.values[lang]:
            return self.values[lang]
        if fallback and "fr" in self.values:
            return self.values["fr"]
        return self.key
