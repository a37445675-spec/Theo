"""
Injection automatique des modules SEO et Traductions - Backend Django.

Usage : python inject_seo_translations_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEO_DIR = os.path.join(BASE_DIR, "apps", "seo")
TRANS_DIR = os.path.join(BASE_DIR, "apps", "translations")


# ============================================================
#                          SEO - FICHIERS
# ============================================================

SEO_MODELS_PY = '''"""Modèles SEO : métadonnées attachables à n'importe quel objet."""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SeoMetadata(models.Model):
    """
    Métadonnées SEO rattachables à n'importe quel modèle via GenericForeignKey.
    Exemple : PageTemplate, Product, BlogPost, Category...
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
    meta_title = models.CharField(max_length=70, blank=True, help_text="60-70 caractères recommandés.")
    meta_description = models.CharField(max_length=160, blank=True, help_text="150-160 caractères recommandés.")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Séparés par des virgules.")

    # Open Graph (Facebook, LinkedIn, WhatsApp)
    og_title = models.CharField(max_length=100, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.ImageField(upload_to="seo/og/", blank=True, null=True)
    og_type = models.CharField(max_length=20, choices=OG_TYPE_CHOICES, default="website")

    # Twitter / X
    twitter_card = models.CharField(
        max_length=20, default="summary_large_image",
        choices=[
            ("summary", "Résumé"),
            ("summary_large_image", "Résumé + grande image"),
        ]
    )

    # Canonique et robots
    canonical_url = models.URLField(blank=True, help_text="URL canonique (laisser vide pour auto).")
    robots = models.CharField(max_length=30, choices=ROBOTS_CHOICES, default="index,follow")

    # JSON-LD (données structurées pour Google)
    structured_data = models.JSONField(default=dict, blank=True, help_text="Format JSON-LD (schema.org).")

    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("content_type", "object_id")
        verbose_name = "Métadonnée SEO"
        verbose_name_plural = "Métadonnées SEO"

    def __str__(self):
        return f"SEO : {self.content_object}"
'''

SEO_SERIALIZERS_PY = '''"""Serializers DRF pour le SEO."""
from rest_framework import serializers
from .models import SeoMetadata


class SeoMetadataSerializer(serializers.ModelSerializer):
    og_image_url = serializers.SerializerMethodField()
    content_object_str = serializers.SerializerMethodField()

    class Meta:
        model = SeoMetadata
        fields = [
            "id", "content_type", "object_id", "content_object_str",
            "meta_title", "meta_description", "meta_keywords",
            "og_title", "og_description", "og_image", "og_image_url", "og_type",
            "twitter_card", "canonical_url", "robots",
            "structured_data", "updated_at",
        ]

    def get_og_image_url(self, obj):
        if obj.og_image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.og_image.url) if request else obj.og_image.url
        return None

    def get_content_object_str(self, obj):
        try:
            return str(obj.content_object)
        except Exception:
            return None
'''

SEO_VIEWS_PY = '''"""Vues API pour le SEO."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from .models import SeoMetadata
from .serializers import SeoMetadataSerializer


class SeoMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API SEO en lecture seule.

    GET /api/v1/seo/metadata/                                → liste
    GET /api/v1/seo/metadata/?content_type=page_template&object_id=1 → détail par objet
    GET /api/v1/seo/metadata/?model=catalog.product&pk=5     → détail (API friendly)
    GET /api/v1/seo/metadata/for-url/?url=/boutique/cosmetiques → résolution par URL
    """
    queryset = SeoMetadata.objects.all()
    serializer_class = SeoMetadataSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        ct = self.request.query_params.get("content_type")
        oid = self.request.query_params.get("object_id")
        if ct and oid:
            qs = qs.filter(content_type__model=ct, object_id=oid)
        return qs

    @action(detail=False, methods=["get"])
    def for_url(self, request):
        """Résout le SEO à partir d'une URL en cherchant dans PageTemplate, Product, BlogPost."""
        url = request.query_params.get("url", "/").rstrip("/") or "/"
        result = None

        # 1. Essayer PageTemplate par slug ou route
        try:
            PageTemplate = apps.get_model("cms", "PageTemplate")
            pt = PageTemplate.objects.filter(slug=url.strip("/")).first()
            if pt:
                result = SeoMetadata.objects.filter(
                    content_type=ContentType.objects.get_for_model(PageTemplate),
                    object_id=pt.id,
                ).first()
        except LookupError:
            pass

        # 2. Essayer Product par slug
        if not result:
            try:
                Product = apps.get_model("catalog", "Product")
                product = Product.objects.filter(slug=url.strip("/").split("/")[-1]).first()
                if product:
                    result = SeoMetadata.objects.filter(
                        content_type=ContentType.objects.get_for_model(Product),
                        object_id=product.id,
                    ).first()
            except LookupError:
                pass

        # 3. Essayer BlogPost par slug
        if not result:
            try:
                Post = apps.get_model("blog", "Post")
                post = Post.objects.filter(slug=url.strip("/").split("/")[-1]).first()
                if post:
                    result = SeoMetadata.objects.filter(
                        content_type=ContentType.objects.get_for_model(Post),
                        object_id=post.id,
                    ).first()
            except LookupError:
                pass

        if not result:
            return Response({"detail": "Aucune métadonnée SEO pour cette URL."}, status=404)

        serializer = self.get_serializer(result)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sitemap(self, request):
        """Génère un sitemap JSON des URLs indexables."""
        urls = []
        try:
            Product = apps.get_model("catalog", "Product")
            for p in Product.objects.filter(status="active"):
                urls.append({"loc": f"/produit/{p.slug}", "changefreq": "weekly"})
        except LookupError:
            pass
        try:
            Post = apps.get_model("blog", "Post")
            for p in Post.objects.filter(status="published"):
                urls.append({"loc": f"/journal/{p.slug}", "changefreq": "monthly"})
        except LookupError:
            pass
        return Response({"urls": urls})
'''

SEO_URLS_PY = '''"""URLs pour le SEO."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SeoMetadataViewSet

router = DefaultRouter()
router.register(r"metadata", SeoMetadataViewSet, basename="seo-metadata")

urlpatterns = [
    path("", include(router.urls)),
]
'''

SEO_ADMIN_PY = '''"""Admin Django pour le SEO."""
from django.contrib import admin
from django.utils.html import format_html
from .models import SeoMetadata


@admin.register(SeoMetadata)
class SeoMetadataAdmin(admin.ModelAdmin):
    list_display = ("content_object_str", "meta_title_preview", "robots", "score", "updated_at")
    list_filter = ("robots", "og_type", "content_type")
    search_fields = ("meta_title", "meta_description", "content_object_str") if False else ("meta_title", "meta_description")
    readonly_fields = ("content_type", "object_id", "updated_at", "seo_preview")

    fieldsets = (
        ("Objet lié", {"fields": ("content_type", "object_id")}),
        ("Balises principales", {"fields": ("meta_title", "meta_description", "meta_keywords")}),
        ("Open Graph", {"fields": ("og_title", "og_description", "og_image", "og_type")}),
        ("Twitter / X", {"fields": ("twitter_card",)}),
        ("Canonique & Robots", {"fields": ("canonical_url", "robots")}),
        ("Données structurées (JSON-LD)", {"fields": ("structured_data",)}),
        ("Métadonnées", {"fields": ("updated_at", "seo_preview")}),
    )

    def content_object_str(self, obj):
        try:
            return str(obj.content_object)
        except Exception:
            return "—"
    content_object_str.short_description = "Objet"

    def meta_title_preview(self, obj):
        return (obj.meta_title or "—")[:60]
    meta_title_preview.short_description = "Titre"

    def score(self, obj):
        """Score SEO basique (0-100)."""
        s = 0
        if obj.meta_title and 30 <= len(obj.meta_title) <= 70:
            s += 25
        if obj.meta_description and 100 <= len(obj.meta_description) <= 160:
            s += 25
        if obj.og_image:
            s += 25
        if obj.structured_data:
            s += 25
        color = "#16A34A" if s >= 75 else ("#D4A843" if s >= 50 else "#DC2626")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:4px;font-weight:600;">{}/100</span>',
            color, s
        )
    score.short_description = "Score SEO"

    def seo_preview(self, obj):
        return format_html(
            '<div style="border:1px solid #ddd;padding:12px;border-radius:8px;max-width:600px;">'
            '<div style="color:#1a0dab;font-size:18px;">{}</div>'
            '<div style="color:#006621;font-size:14px;">{}</div>'
            '<div style="color:#545454;font-size:13px;">{}</div>'
            '</div>',
            obj.meta_title or "(titre vide)",
            obj.canonical_url or "https://nawa.com/...",
            obj.meta_description or "(description vide)",
        )
    seo_preview.short_description = "Aperçu Google"
'''

SEO_APPS_PY = '''"""Configuration de l'application SEO."""
from django.apps import AppConfig


class SeoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.seo"
    verbose_name = "SEO & Métadonnées"
'''


# ============================================================
#                     TRADUCTIONS - FICHIERS
# ============================================================

TRANS_MODELS_PY = '''"""Modèles pour les traductions (i18n pilotable depuis l'admin)."""
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
'''

TRANS_SERIALIZERS_PY = '''"""Serializers DRF pour les traductions."""
from rest_framework import serializers
from .models import TranslationKey


class TranslationKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationKey
        fields = ["id", "key", "values", "context", "description", "is_active"]
'''

TRANS_VIEWS_PY = '''"""Vues API pour les traductions."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import TranslationKey
from .serializers import TranslationKeySerializer


class TranslationKeyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API Traductions.

    GET /api/v1/translations/                    → liste complète
    GET /api/v1/translations/?lang=fr            → objet { "key": "value", ... } prêt à consommer
    GET /api/v1/translations/?context=Panier     → filtré par contexte
    GET /api/v1/translations/languages/          → liste des langues disponibles
    """
    queryset = TranslationKey.objects.filter(is_active=True)
    serializer_class = TranslationKeySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        context = self.request.query_params.get("context")
        if context:
            qs = qs.filter(context=context)
        return qs

    def list(self, request, *args, **kwargs):
        """Si ?lang= est fourni, on renvoie un objet plat { key: value }."""
        lang = request.query_params.get("lang")
        if lang:
            qs = self.get_queryset()
            data = {t.key: t.get_value(lang) for t in qs}
            return Response(data)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def languages(self, request):
        """Liste toutes les langues disponibles."""
        langs = set()
        for t in self.get_queryset():
            langs.update((t.values or {}).keys())
        return Response(sorted(langs))
'''

TRANS_URLS_PY = '''"""URLs pour les traductions."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TranslationKeyViewSet

router = DefaultRouter()
router.register(r"", TranslationKeyViewSet, basename="translation")

urlpatterns = [
    path("", include(router.urls)),
]
'''

TRANS_ADMIN_PY = '''"""Admin Django pour les traductions."""
from django.contrib import admin
from django.utils.html import format_html
from .models import TranslationKey


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    list_display = ("key", "context", "preview_fr", "preview_en", "is_active", "updated_at")
    list_filter = ("context", "is_active")
    search_fields = ("key", "context", "description")
    list_editable = ("is_active",)
    ordering = ("key",)

    fieldsets = (
        ("Identification", {"fields": ("key", "context", "description")}),
        ("Traductions (JSON)", {
            "fields": ("values",),
            "description": 'Format attendu : {"fr": "Bonjour", "en": "Hello"}'
        }),
        ("Statut", {"fields": ("is_active",)}),
    )

    def preview_fr(self, obj):
        return (obj.values or {}).get("fr", "—")[:60]
    preview_fr.short_description = "Français"

    def preview_en(self, obj):
        return (obj.values or {}).get("en", "—")[:60]
    preview_en.short_description = "Anglais"
'''

TRANS_APPS_PY = '''"""Configuration de l'application Traductions."""
from django.apps import AppConfig


class TranslationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.translations"
    verbose_name = "Traductions"
'''

TRANS_SEED_PY = '''"""Crée les clés de traduction de base."""
from django.core.management.base import BaseCommand
from apps.translations.models import TranslationKey


DEFAULT_KEYS = [
    # (key, fr, en, context, description)
    ("common.loading", "Chargement…", "Loading…", "Global", ""),
    ("common.error", "Une erreur est survenue.", "An error occurred.", "Global", ""),
    ("common.retry", "Réessayer", "Try again", "Global", ""),
    ("common.close", "Fermer", "Close", "Global", ""),
    ("common.search", "Rechercher", "Search", "Global", ""),
    ("common.cancel", "Annuler", "Cancel", "Global", ""),
    ("common.save", "Enregistrer", "Save", "Global", ""),
    ("common.delete", "Supprimer", "Delete", "Global", ""),
    ("common.confirm", "Confirmer", "Confirm", "Global", ""),

    ("nav.shop", "Boutique", "Shop", "Navigation", ""),
    ("nav.journal", "Journal", "Blog", "Navigation", ""),
    ("nav.account", "Mon compte", "My account", "Navigation", ""),
    ("nav.cart", "Panier", "Cart", "Navigation", ""),

    ("cart.empty.title", "Votre panier est vide", "Your cart is empty", "Panier", ""),
    ("cart.empty.cta", "Découvrir la boutique", "Browse the shop", "Panier", ""),
    ("cart.checkout", "Passer commande", "Checkout", "Panier", ""),
    ("cart.subtotal", "Sous-total", "Subtotal", "Panier", ""),
    ("cart.shipping", "Livraison", "Shipping", "Panier", ""),
    ("cart.total", "Total", "Total", "Panier", ""),

    ("checkout.title", "Finaliser la commande", "Complete your order", "Commande", ""),
    ("checkout.payment", "Paiement", "Payment", "Commande", ""),
    ("checkout.address", "Adresse de livraison", "Shipping address", "Commande", ""),
    ("checkout.success", "Merci pour votre commande !", "Thank you for your order!", "Commande", ""),

    ("auth.login", "Connexion", "Sign in", "Authentification", ""),
    ("auth.register", "Créer un compte", "Sign up", "Authentification", ""),
    ("auth.logout", "Se déconnecter", "Sign out", "Authentification", ""),
    ("auth.email", "Adresse email", "Email address", "Authentification", ""),
    ("auth.password", "Mot de passe", "Password", "Authentification", ""),
    ("auth.forgot", "Mot de passe oublié ?", "Forgot password?", "Authentification", ""),

    ("product.add_to_cart", "Ajouter au panier", "Add to cart", "Produit", ""),
    ("product.out_of_stock", "Rupture de stock", "Out of stock", "Produit", ""),
    ("product.reviews", "Avis clients", "Customer reviews", "Produit", ""),
    ("product.description", "Description", "Description", "Produit", ""),
    ("product.shipping_info", "Livraison & retours", "Shipping & returns", "Produit", ""),

    ("footer.about", "À propos", "About", "Pied de page", ""),
    ("footer.contact", "Contact", "Contact", "Pied de page", ""),
    ("footer.legal", "Mentions légales", "Legal notice", "Pied de page", ""),
    ("footer.privacy", "Confidentialité", "Privacy", "Pied de page", ""),

    ("empty.no_results", "Aucun résultat", "No results", "États vides", ""),
    ("empty.no_orders", "Aucune commande pour le moment", "No orders yet", "États vides", ""),
    ("empty.no_products", "Aucun produit disponible", "No products available", "États vides", ""),
]


class Command(BaseCommand):
    help = "Crée les clés de traduction par défaut (FR/EN)."

    def handle(self, *args, **options):
        created_count = 0
        for key, fr, en, ctx, desc in DEFAULT_KEYS:
            obj, created = TranslationKey.objects.update_or_create(
                key=key,
                defaults={
                    "values": {"fr": fr, "en": en},
                    "context": ctx,
                    "description": desc,
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created_count} nouvelles clés créées, {len(DEFAULT_KEYS)} au total."
        ))
'''


# ============================================================
#                        UTILITAIRES
# ============================================================

def ensure_init(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")


def write_file(path, content):
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def find_settings():
    for c in [
        os.path.join(BASE_DIR, "config", "settings.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "settings.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def find_urls():
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def add_to_settings(app_paths):
    """Ajoute les apps dans LOCAL_APPS (ou INSTALLED_APPS)."""
    settings = find_settings()
    if not settings:
        print("  [ERREUR] settings.py introuvable.")
        return False

    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()

    new_apps = [a for a in app_paths if f'"{a}"' not in content]
    if not new_apps:
        print("  [SKIP] apps déjà dans settings.py")
        return True

    shutil.copy2(settings, settings + ".bak")

    target = None
    for name in ("LOCAL_APPS", "INSTALLED_APPS"):
        m = re.search(rf"{name}\s*[:=]\s*\[(.*?)\]", content, re.DOTALL)
        if m:
            target = (name, m)
            break

    if not target:
        print("  [ATTENTION] LOCAL_APPS/INSTALLED_APPS introuvable.")
        return False

    name, m = target
    insertion = "".join(f'\n    "{a}",' for a in new_apps) + "\n"
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(settings, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] {len(new_apps)} apps ajoutées à {name}")
    return True


def add_url_routes(routes):
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return False

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    existing = [r for r in routes if r[1] in content]
    if existing:
        print("  [SKIP] certaines routes existent déjà")
        return True

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        print("  [ATTENTION] urlpatterns introuvable.")
        return False

    insertion = "\n    # === SEO & Traductions ===\n"
    for name, path in routes:
        insertion += f'    path("{path}", include("{name}")),\n'

    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] {len(routes)} routes ajoutées")
    return True


def run_cmd(*args, allow_fail=False):
    try:
        subprocess.run([sys.executable, "manage.py", *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        if not allow_fail:
            sys.exit(1)


def main():
    print("=" * 60)
    print("  INJECTION SEO + TRADUCTIONS - BACKEND")
    print("=" * 60)

    # ---------- SEO ----------
    print("\n1. Création des fichiers SEO...")
    for sub in ["", "migrations"]:
        ensure_init(os.path.join(SEO_DIR, sub, "__init__.py"))
    write_file(os.path.join(SEO_DIR, "models.py"), SEO_MODELS_PY)
    write_file(os.path.join(SEO_DIR, "serializers.py"), SEO_SERIALIZERS_PY)
    write_file(os.path.join(SEO_DIR, "views.py"), SEO_VIEWS_PY)
    write_file(os.path.join(SEO_DIR, "urls.py"), SEO_URLS_PY)
    write_file(os.path.join(SEO_DIR, "admin.py"), SEO_ADMIN_PY)
    write_file(os.path.join(SEO_DIR, "apps.py"), SEO_APPS_PY)

    # ---------- TRADUCTIONS ----------
    print("\n2. Création des fichiers Traductions...")
    for sub in ["", "migrations", "management", "management/commands"]:
        ensure_init(os.path.join(TRANS_DIR, sub, "__init__.py"))
    write_file(os.path.join(TRANS_DIR, "models.py"), TRANS_MODELS_PY)
    write_file(os.path.join(TRANS_DIR, "serializers.py"), TRANS_SERIALIZERS_PY)
    write_file(os.path.join(TRANS_DIR, "views.py"), TRANS_VIEWS_PY)
    write_file(os.path.join(TRANS_DIR, "urls.py"), TRANS_URLS_PY)
    write_file(os.path.join(TRANS_DIR, "admin.py"), TRANS_ADMIN_PY)
    write_file(os.path.join(TRANS_DIR, "apps.py"), TRANS_APPS_PY)
    write_file(os.path.join(TRANS_DIR, "management", "commands", "seed_translations.py"), TRANS_SEED_PY)

    # ---------- SETTINGS ----------
    print("\n3. Mise à jour de settings.py...")
    add_to_settings(["apps.seo", "apps.translations"])

    # ---------- URLS ----------
    print("\n4. Mise à jour de urls.py...")
    add_url_routes([
        ("apps.seo.urls", "api/v1/seo/"),
        ("apps.translations.urls", "api/v1/translations/"),
    ])

    # ---------- MIGRATIONS ----------
    print("\n5. Migrations...")
    run_cmd("makemigrations", "seo", "translations", allow_fail=True)
    run_cmd("migrate")

    # ---------- SEED ----------
    print("\n6. Seed des traductions...")
    run_cmd("seed_translations", allow_fail=True)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nEndpoints disponibles :")
    print("  SEO         : http://127.0.0.1:8000/api/v1/seo/metadata/")
    print("  Sitemap     : http://127.0.0.1:8000/api/v1/seo/metadata/sitemap/")
    print("  Traductions : http://127.0.0.1:8000/api/v1/translations/?lang=fr")
    print("  Langues     : http://127.0.0.1:8000/api/v1/translations/languages/")
    print("\nAdmin :")
    print("  SEO         : http://127.0.0.1:8000/admin/seo/seometadata/")
    print("  Traductions : http://127.0.0.1:8000/admin/translations/translationkey/")


if __name__ == "__main__":
    main()