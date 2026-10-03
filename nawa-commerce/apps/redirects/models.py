"""Modèles pour les redirections URL dynamiques."""
from django.db import models


class Redirect(models.Model):
    """Une redirection 301/302 configurable depuis l'admin."""

    REDIRECT_TYPE_CHOICES = [
        ("301", "301 — Permanent (SEO)"),
        ("302", "302 — Temporaire"),
    ]

    old_path = models.CharField(
        max_length=500, unique=True,
        verbose_name="Ancien chemin",
        help_text="Ex: /ancienne-url (sans le domaine)"
    )
    new_path = models.CharField(
        max_length=500,
        verbose_name="Nouveau chemin",
        help_text="Ex: /nouvelle-url ou https://externe.com"
    )
    redirect_type = models.CharField(
        max_length=3, choices=REDIRECT_TYPE_CHOICES, default="301"
    )
    is_active = models.BooleanField(default=True)
    hit_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de visites")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Redirection"
        verbose_name_plural = "Redirections"

    def __str__(self):
        return f"{self.old_path} → {self.new_path} ({self.redirect_type})"

    def save(self, *args, **kwargs):
        # Normalisation : toujours commencer par /
        if self.old_path and not self.old_path.startswith("/"):
            self.old_path = "/" + self.old_path
        super().save(*args, **kwargs)
