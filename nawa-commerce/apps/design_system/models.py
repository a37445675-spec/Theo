"""Modèles pour le Design System (couleurs, typographie, formes)."""
from django.core.validators import RegexValidator
from django.db import models


HEX_VALIDATOR = RegexValidator(
    regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
    message="Entrez une couleur hexadécimale valide (ex: #C1652F)."
)


class DesignSystem(models.Model):
    """Configuration globale du design (une seule instance active)."""

    name = models.CharField(max_length=100, default="NAWA Design System")
    is_active = models.BooleanField(default=True, help_text="Un seul design system peut être actif à la fois.")

    # === COULEURS ===
    color_primary = models.CharField(max_length=7, default="#C1652F", validators=[HEX_VALIDATOR], verbose_name="Couleur primaire")
    color_secondary = models.CharField(max_length=7, default="#2F4A3C", validators=[HEX_VALIDATOR], verbose_name="Couleur secondaire")
    color_background = models.CharField(max_length=7, default="#F7F0E4", validators=[HEX_VALIDATOR], verbose_name="Fond de page")
    color_surface = models.CharField(max_length=7, default="#FFFFFF", validators=[HEX_VALIDATOR], verbose_name="Surface (cartes)")
    color_text = models.CharField(max_length=7, default="#221B15", validators=[HEX_VALIDATOR], verbose_name="Texte principal")
    color_text_muted = models.CharField(max_length=7, default="#6B6259", validators=[HEX_VALIDATOR], verbose_name="Texte secondaire")
    color_accent = models.CharField(max_length=7, default="#D4A843", validators=[HEX_VALIDATOR], verbose_name="Couleur d'accent (or)")
    color_error = models.CharField(max_length=7, default="#DC2626", validators=[HEX_VALIDATOR], verbose_name="Erreur")
    color_success = models.CharField(max_length=7, default="#16A34A", validators=[HEX_VALIDATOR], verbose_name="Succès")

    # === TYPOGRAPHIE ===
    font_heading = models.CharField(max_length=100, default="Fraunces", verbose_name="Police des titres", help_text="Nom de la police Google Fonts (ex: Fraunces).")
    font_body = models.CharField(max_length=100, default="Sora", verbose_name="Police du corps", help_text="Nom de la police Google Fonts (ex: Sora, Inter).")
    font_size_base = models.CharField(max_length=20, default="16px", verbose_name="Taille de base")
    font_size_h1 = models.CharField(max_length=20, default="3.5rem", verbose_name="Taille H1")
    font_size_h2 = models.CharField(max_length=20, default="2.5rem", verbose_name="Taille H2")
    font_size_h3 = models.CharField(max_length=20, default="1.75rem", verbose_name="Taille H3")
    line_height = models.CharField(max_length=10, default="1.6", verbose_name="Hauteur de ligne")

    # === FORMES ===
    border_radius = models.CharField(max_length=20, default="16px", verbose_name="Rayon des bordures")
    button_radius = models.CharField(max_length=20, default="999px", verbose_name="Rayon des boutons")
    card_radius = models.CharField(max_length=20, default="16px", verbose_name="Rayon des cartes")

    # === OMBRES ===
    shadow_sm = models.CharField(max_length=100, default="0 1px 2px rgba(0,0,0,0.05)", verbose_name="Ombre petite")
    shadow_md = models.CharField(max_length=100, default="0 4px 12px rgba(0,0,0,0.10)", verbose_name="Ombre moyenne")
    shadow_lg = models.CharField(max_length=100, default="0 10px 30px rgba(0,0,0,0.15)", verbose_name="Ombre grande")

    # === AVANCÉ ===
    custom_css = models.TextField(blank=True, verbose_name="CSS personnalisé", help_text="CSS additionnel injecté dans le <head> (avancé).")

    # === MÉTADONNÉES ===
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Design System"
        verbose_name_plural = "Design System"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            DesignSystem.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        obj = cls.objects.filter(is_active=True).first()
        if not obj:
            obj = cls.objects.create()
        return obj
