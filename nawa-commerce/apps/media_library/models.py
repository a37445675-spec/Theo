"""Modèles pour la médiathèque centralisée."""
import mimetypes
import os

from django.db import models
from django.utils.text import slugify
from PIL import Image


class MediaTag(models.Model):
    """Étiquette pour catégoriser les médias."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    color = models.CharField(max_length=7, default="#6B6259")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Étiquette média"
        verbose_name_plural = "Étiquettes média"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MediaAsset(models.Model):
    """
    Un média (image, vidéo, PDF...) uploadé une seule fois et réutilisable partout.
    Contient les métadonnées utiles pour le SEO et l'affichage.
    """

    FILE_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Vidéo"),
        ("pdf", "PDF"),
        ("document", "Document"),
        ("other", "Autre"),
    ]

    # === Fichier ===
    file = models.FileField(upload_to="media-library/%Y/%m/", verbose_name="Fichier")
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default="image")
    mime_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="Taille en octets")

    # === Métadonnées ===
    name = models.CharField(max_length=200, verbose_name="Nom")
    alt_text = models.CharField(
        max_length=255, blank=True,
        verbose_name="Texte alternatif",
        help_text="Important pour le SEO et l'accessibilité."
    )
    caption = models.TextField(blank=True, verbose_name="Légende")

    # === Dimensions (uniquement pour les images) ===
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    # === Catégorisation ===
    tags = models.ManyToManyField(MediaTag, blank=True, related_name="assets")

    # === Métadonnées système ===
    uploaded_by = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="uploaded_media"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Média"
        verbose_name_plural = "Médiathèque"

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        # Détection automatique du type et de la taille
        if self.file:
            # MIME type
            if not self.mime_type:
                self.mime_type = mimetypes.guess_type(self.file.name)[0] or "application/octet-stream"

            # File size
            try:
                self.file_size = self.file.size
            except (OSError, ValueError):
                pass

            # File type
            if not self.file_type or self.file_type == "other":
                if self.mime_type.startswith("image/"):
                    self.file_type = "image"
                elif self.mime_type.startswith("video/"):
                    self.file_type = "video"
                elif self.mime_type == "application/pdf":
                    self.file_type = "pdf"
                else:
                    self.file_type = "document"

            # Dimensions (pour les images)
            if self.file_type == "image" and (not self.width or not self.height):
                try:
                    with Image.open(self.file) as img:
                        self.width, self.height = img.size
                except Exception:
                    pass

        super().save(*args, **kwargs)

    @property
    def extension(self):
        return os.path.splitext(self.file.name)[1].lower().lstrip(".")

    @property
    def file_size_human(self):
        """Retourne la taille en Ko/Mo lisible."""
        size = self.file_size
        for unit in ["o", "Ko", "Mo", "Go"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"

    @property
    def ratio(self):
        if self.width and self.height:
            return round(self.width / self.height, 2)
        return None
