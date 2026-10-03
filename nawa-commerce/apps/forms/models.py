"""Modèles pour les formulaires dynamiques (pilotés depuis l'admin)."""
from django.db import models


class FormDefinition(models.Model):
    """
    Définition d'un formulaire (contact, newsletter, devis...).
    Peut contenir N champs (FormField) et recevoir N soumissions (FormSubmission).
    """

    name = models.CharField(max_length=100, verbose_name="Nom du formulaire")
    slug = models.SlugField(
        max_length=100, unique=True,
        help_text="Identifiant technique (ex: contact, newsletter)."
    )
    description = models.TextField(blank=True, verbose_name="Description")

    # === Comportement après soumission ===
    success_message = models.TextField(
        default="Merci, votre message a bien été envoyé.",
        verbose_name="Message de succès"
    )
    redirect_url = models.CharField(
        max_length=500, blank=True,
        verbose_name="URL de redirection",
        help_text="Si vide, le message de succès s'affiche sur place."
    )
    email_notification = models.EmailField(
        blank=True,
        verbose_name="Email de notification",
        help_text="Adresse qui reçoit un email à chaque soumission."
    )

    # === Anti-spam ===
    captcha_enabled = models.BooleanField(default=False, verbose_name="Activer le CAPTCHA")

    # === Statut ===
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Formulaire"
        verbose_name_plural = "Formulaires"

    def __str__(self):
        return f"{self.name} ({self.slug})"


class FormField(models.Model):
    """Un champ d'un formulaire dynamique."""

    FIELD_TYPE_CHOICES = [
        ("text", "Texte court"),
        ("textarea", "Texte long"),
        ("email", "Email"),
        ("phone", "Téléphone"),
        ("number", "Nombre"),
        ("date", "Date"),
        ("select", "Liste déroulante"),
        ("radio", "Boutons radio"),
        ("checkbox", "Case à cocher"),
        ("file", "Fichier"),
    ]

    form = models.ForeignKey(
        FormDefinition, on_delete=models.CASCADE, related_name="fields"
    )
    label = models.CharField(max_length=200, verbose_name="Libellé")
    field_key = models.SlugField(
        max_length=100,
        verbose_name="Clé technique",
        help_text="Identifiant du champ dans le formulaire (ex: nom, email)."
    )
    field_type = models.CharField(
        max_length=20, choices=FIELD_TYPE_CHOICES, default="text"
    )

    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.CharField(max_length=255, blank=True, verbose_name="Texte d'aide")
    is_required = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, blank=True)
    options = models.JSONField(
        default=list, blank=True,
        help_text='Pour les listes/radios : [{"value": "a", "label": "Option A"}, ...]'
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("form", "field_key")
        verbose_name = "Champ de formulaire"
        verbose_name_plural = "Champs de formulaire"

    def __str__(self):
        return f"{self.label} ({self.get_field_type_display()})"


class FormSubmission(models.Model):
    """Une soumission d'un formulaire."""

    STATUS_CHOICES = [
        ("new", "Nouveau"),
        ("read", "Lu"),
        ("replied", "Répondu"),
        ("archived", "Archivé"),
        ("spam", "Spam"),
    ]

    form = models.ForeignKey(
        FormDefinition, on_delete=models.CASCADE, related_name="submissions"
    )
    data = models.JSONField(default=dict, help_text="Données soumises (clé/valeur)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referer = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="form_submissions"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"

    def __str__(self):
        return f"{self.form.name} — {self.created_at:%d/%m/%Y %H:%M}"
