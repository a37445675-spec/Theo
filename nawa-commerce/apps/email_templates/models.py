"""Modèles pour les templates d'emails transactionnels."""
from django.db import models


class EmailTemplate(models.Model):
    """Un template d'email modifiable depuis l'admin."""

    code = models.SlugField(
        max_length=100, unique=True,
        verbose_name="Code",
        help_text="Identifiant technique (ex: order_confirmation, welcome)."
    )
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")

    subject = models.CharField(max_length=255, verbose_name="Sujet")
    body_text = models.TextField(
        blank=True, verbose_name="Version texte",
        help_text="Version plain-text (recommandée pour la délivrabilité)."
    )
    body_html = models.TextField(
        blank=True, verbose_name="Version HTML",
        help_text="Version HTML avec mise en forme."
    )

    from_email = models.EmailField(
        blank=True, default="",
        verbose_name="Email expéditeur",
        help_text="Vide = utilise DEFAULT_FROM_EMAIL."
    )

    variables = models.JSONField(
        default=list, blank=True,
        verbose_name="Variables disponibles",
        help_text='Ex: ["user_name", "order_id", "total"]'
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Template d'email"
        verbose_name_plural = "Templates d'emails"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def render(self, context):
        """Rend le sujet et le corps avec les variables fournies."""
        from django.template import Template, Context
        ctx = Context(context)
        return {
            "subject": Template(self.subject).render(ctx),
            "body_text": Template(self.body_text).render(ctx) if self.body_text else "",
            "body_html": Template(self.body_html).render(ctx) if self.body_html else "",
        }
