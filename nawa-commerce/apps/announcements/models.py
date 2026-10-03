"""Modèles pour les Annonces et Bannières (promos, infos)."""
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    """
    Une annonce à afficher dans le site.
    Peut apparaître en haut de page, en bas, ou en popup central.
    """

    POSITION_CHOICES = [
        ("top_bar", "Bandeau supérieur"),
        ("bottom", "Bandeau inférieur"),
        ("popup", "Popup central"),
        ("floating", "Bulle flottante"),
    ]

    # === Contenu ===
    message = models.CharField(max_length=500, verbose_name="Message")
    link = models.URLField(blank=True, verbose_name="Lien")
    link_label = models.CharField(
        max_length=100, blank=True,
        verbose_name="Texte du lien",
        help_text="Ex: 'En savoir plus', 'Profiter de l\'offre'"
    )

    # === Style ===
    background_color = models.CharField(
        max_length=7, default="#C1652F",
        verbose_name="Couleur de fond"
    )
    text_color = models.CharField(
        max_length=7, default="#FFFFFF",
        verbose_name="Couleur du texte"
    )
    icon = models.ImageField(
        upload_to="announcements/icons/",
        blank=True, null=True,
        verbose_name="Icône (optionnelle)"
    )

    # === Ciblage ===
    position = models.CharField(
        max_length=20, choices=POSITION_CHOICES,
        default="top_bar", verbose_name="Position"
    )
    target_audience = models.CharField(
        max_length=20, default="all",
        choices=[
            ("all", "Tout le monde"),
            ("anonymous", "Visiteurs non connectés"),
            ("authenticated", "Utilisateurs connectés"),
        ],
        verbose_name="Audience cible"
    )
    target_pages = models.CharField(
        max_length=500, blank=True,
        verbose_name="Pages ciblées",
        help_text="Vide = toutes les pages. Sinon, URLs séparées par des virgules (ex: /, /boutique/cosmetiques)."
    )

    # === Programmation ===
    starts_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Début (optionnel)"
    )
    ends_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fin (optionnel)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activée"
    )

    # === Ordre ===
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Priorité",
        help_text="Plus petit = affiché en premier."
    )

    # === Métadonnées ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"

    def __str__(self):
        return f"{self.message[:60]} ({self.get_position_display()})"

    @property
    def is_currently_active(self):
        """Vérifie si l'annonce est active ET dans sa plage de dates."""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True
