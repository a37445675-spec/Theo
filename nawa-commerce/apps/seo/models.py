"""Modèles SEO : mixin abstrait + métadonnées génériques."""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# ============================================================
#               MIXIN (hérité par les modèles métier)
# ============================================================

class SEOFieldsMixin(models.Model):
    """
    Mixin abstrait à hériter dans tout modèle métier (Product, Post, Category...)
    pour activer les champs SEO directement sur le modèle.
    """
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True)
    noindex = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def resolved_meta_title(self, fallback: str) -> str:
        return self.meta_title or fallback

    def resolved_meta_description(self, fallback: str = "") -> str:
        return self.meta_description or fallback


# ============================================================
#               HELPERS JSON-LD (données structurées)
# ============================================================

def product_json_ld(product, request=None) -> dict:
    """Génère le JSON-LD schema.org pour un produit."""
    image_urls = [img.image.url for img in product.images.all()[:5]]
    if request:
        image_urls = [request.build_absolute_uri(u) for u in image_urls]

    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "sku": product.sku,
        "description": product.short_description or product.description,
        "image": image_urls,
        "brand": (
            {"@type": "Brand", "name": product.brand.name}
            if product.brand_id else None
        ),
        "offers": {
            "@type": "Offer",
            "price": str(product.price),
            "priceCurrency": product.currency,
            "availability": (
                "https://schema.org/InStock"
                if product.in_stock else "https://schema.org/OutOfStock"
            ),
        },
        "aggregateRating": (
            {
                "@type": "AggregateRating",
                "ratingValue": str(product.rating_average),
                "reviewCount": product.reviews_count,
            }
            if product.reviews_count else None
        ),
    }


# ============================================================
#               MÉTADONNÉES SEO GÉNÉRIQUES (CMS Headless)
# ============================================================

class SeoMetadata(models.Model):
    """
    Métadonnées SEO rattachables à n'importe quel modèle via GenericForeignKey.
    Complète le mixin SEOFieldsMixin pour les objets qui ne peuvent pas en hériter
    (ex: PageTemplate, PageBlock...).
    """

    ROBOTS_CHOICES = [
        ("index,follow", "Indexer + Suivre (par défaut)"),
        ("index,nofollow", "Indexer + Ne pas suivre"),
        ("noindex,follow", "Ne pas indexer + Suivre"),
        ("noindex,nofollow", "Ne pas indexer + Ne pas suivre"),
    ]

    OG_TYPE_CHOICES = [
        ("website", "Site web"),
        ("article", "Article"),
        ("product", "Produit"),
        ("profile", "Profil"),
        ("video.other", "Vidéo"),
    ]

    # Lien générique
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Balises principales
    meta_title = models.CharField(
        max_length=70, blank=True,
        help_text="60-70 caractères recommandés."
    )
    meta_description = models.CharField(
        max_length=160, blank=True,
        help_text="150-160 caractères recommandés."
    )
    meta_keywords = models.CharField(
        max_length=255, blank=True,
        help_text="Séparés par des virgules."
    )

    # Open Graph (Facebook, LinkedIn, WhatsApp)
    og_title = models.CharField(max_length=100, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.ImageField(upload_to="seo/og/", blank=True, null=True)
    og_type = models.CharField(
        max_length=20, choices=OG_TYPE_CHOICES, default="website"
    )

    # Twitter / X
    twitter_card = models.CharField(
        max_length=20, default="summary_large_image",
        choices=[
            ("summary", "Résumé"),
            ("summary_large_image", "Résumé + grande image"),
        ]
    )

    # Canonique et robots
    canonical_url = models.URLField(
        blank=True,
        help_text="URL canonique (laisser vide pour auto)."
    )
    robots = models.CharField(
        max_length=30, choices=ROBOTS_CHOICES, default="index,follow"
    )

    # JSON-LD (données structurées pour Google)
    structured_data = models.JSONField(
        default=dict, blank=True,
        help_text="Format JSON-LD (schema.org)."
    )

    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("content_type", "object_id")
        verbose_name = "Métadonnée SEO"
        verbose_name_plural = "Métadonnées SEO"

    def __str__(self):
        try:
            return f"SEO : {self.content_object}"
        except Exception:
            return f"SEO #{self.pk}"