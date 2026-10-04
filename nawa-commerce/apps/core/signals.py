
# ============================================================
#  PURGE AUTOMATIQUE DU CACHE (backend)
# ============================================================

"""
Signaux Django qui vident le cache quand on modifie
les modèles critiques (menus, annonces, flags, design system).
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


@receiver([post_save, post_delete])
def invalidate_navigation_cache(sender, instance, **kwargs):
    """Purge le cache quand un Menu ou MenuItem change."""
    if sender.__name__ in ("Menu", "MenuItem"):
        _purge_api_cache("navigation")


@receiver([post_save, post_delete])
def invalidate_announcement_cache(sender, instance, **kwargs):
    """Purge le cache quand une Annonce change."""
    if sender.__name__ in ("Announcement",):
        _purge_api_cache("announcements")


@receiver([post_save, post_delete])
def invalidate_design_system_cache(sender, instance, **kwargs):
    """Purge le cache quand le Design System change."""
    if sender.__name__ in ("DesignSystem",):
        _purge_api_cache("design-system")


@receiver([post_save, post_delete])
def invalidate_feature_flags_cache(sender, instance, **kwargs):
    """Purge le cache quand un Feature Flag change."""
    if sender.__name__ in ("FeatureFlag",):
        _purge_api_cache("feature-flags")


@receiver([post_save, post_delete])
def invalidate_catalog_cache(sender, instance, **kwargs):
    """Purge le cache quand un produit ou une catégorie change."""
    if sender.__name__ in ("Product", "ProductVariant", "Category", "Brand"):
        _purge_api_cache("catalog")


@receiver([post_save, post_delete])
def invalidate_blog_cache(sender, instance, **kwargs):
    """Purge le cache quand un article ou une catégorie de blog change."""
    if sender.__name__ in ("Post", "BlogCategory", "BlogTag", "Comment"):
        _purge_api_cache("blog")


def _purge_api_cache(prefix):
    """
    Purge le cache Redis pour toutes les URLs commençant par
    /api/v1/{prefix}/. Comme Django ne permet pas une purge par préfixe
    nativement, on utilise une clé « version » qu'on incrémente.
    """
    try:
        key = f"cache_version:{prefix}"
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=None)
    except Exception:
        pass
