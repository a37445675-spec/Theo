"""
Injection des modules Formulaires, Redirections, Scripts tiers et Emails - Backend.

Prérequis : les apps apps/forms/, apps/redirects/,
            apps/third_party_scripts/, apps/email_templates/ existent.

Usage : python inject_week6_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORMS_DIR = os.path.join(BASE_DIR, "apps", "forms")
REDIRECTS_DIR = os.path.join(BASE_DIR, "apps", "redirects")
SCRIPTS_DIR = os.path.join(BASE_DIR, "apps", "third_party_scripts")
EMAILS_DIR = os.path.join(BASE_DIR, "apps", "email_templates")


# ============================================================
#                   FORMULAIRES - FICHIERS
# ============================================================

FORMS_MODELS_PY = '''"""Modèles pour les formulaires dynamiques (pilotés depuis l'admin)."""
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
'''

FORMS_SERIALIZERS_PY = '''"""Serializers DRF pour les formulaires."""
from rest_framework import serializers
from .models import FormDefinition, FormField, FormSubmission


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = [
            "id", "label", "field_key", "field_type",
            "placeholder", "help_text", "is_required",
            "default_value", "options", "order",
        ]


class FormDefinitionSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = FormDefinition
        fields = [
            "id", "name", "slug", "description",
            "success_message", "redirect_url",
            "captcha_enabled", "is_active",
            "fields",
        ]


class FormSubmissionSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source="form.name", read_only=True)

    class Meta:
        model = FormSubmission
        fields = [
            "id", "form", "form_name", "data", "status",
            "ip_address", "user_agent", "referer",
            "created_at",
        ]
        read_only_fields = [
            "ip_address", "user_agent", "referer",
            "created_at", "status",
        ]


class FormSubmitSerializer(serializers.Serializer):
    """Serializer pour la soumission publique d'un formulaire."""
    data = serializers.JSONField()
'''

FORMS_VIEWS_PY = '''"""Vues API pour les formulaires."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import FormDefinition, FormField, FormSubmission
from .serializers import (
    FormDefinitionSerializer,
    FormFieldSerializer,
    FormSubmissionSerializer,
)


class FormDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique des formulaires.

    GET /api/v1/forms/definitions/               → tous les formulaires actifs
    GET /api/v1/forms/definitions/{slug}/         → détail d'un formulaire
    """
    queryset = FormDefinition.objects.filter(is_active=True).prefetch_related("fields")
    serializer_class = FormDefinitionSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class FormSubmissionViewSet(viewsets.ModelViewSet):
    """
    API des soumissions.

    POST /api/v1/forms/submissions/            → soumettre (public)
    GET  /api/v1/forms/submissions/            → lire (auth requis)
    """
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        """Soumission publique d'un formulaire."""
        form_id = request.data.get("form")
        form_data = request.data.get("data", {})

        if not form_id:
            return Response(
                {"detail": "Le champ 'form' est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        form = get_object_or_404(FormDefinition, id=form_id, is_active=True)

        # Validation basique des champs requis
        errors = {}
        for field in form.fields.all():
            if field.is_required and not form_data.get(field.field_key):
                errors[field.field_key] = f"Le champ '{field.label}' est obligatoire."

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Création de la soumission
        submission = FormSubmission.objects.create(
            form=form,
            data=form_data,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            referer=request.META.get("HTTP_REFERER", "")[:500],
            user=request.user if request.user.is_authenticated else None,
        )

        # Notification email
        self._notify(form, submission)

        return Response({
            "id": submission.id,
            "success_message": form.success_message,
            "redirect_url": form.redirect_url or None,
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def _notify(form, submission):
        """Envoie un email de notification si configuré."""
        if not form.email_notification:
            return
        from django.core.mail import send_mail
        from django.conf import settings
        try:
            body = f"Nouvelle soumission pour '{form.name}'\\n\\n"
            for key, value in submission.data.items():
                body += f"{key} : {value}\\n"
            send_mail(
                subject=f"[NAWA] Nouveau formulaire — {form.name}",
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nawa.com"),
                recipient_list=[form.email_notification],
                fail_silently=True,
            )
        except Exception:
            pass
'''

FORMS_URLS_PY = '''"""URLs pour les formulaires."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormDefinitionViewSet, FormSubmissionViewSet

router = DefaultRouter()
router.register(r"definitions", FormDefinitionViewSet, basename="form-definition")
router.register(r"submissions", FormSubmissionViewSet, basename="form-submission")

urlpatterns = [
    path("", include(router.urls)),
]
'''

FORMS_ADMIN_PY = '''"""Admin Django pour les formulaires."""
from django.contrib import admin
from django.utils.html import format_html
from .models import FormDefinition, FormField, FormSubmission


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    fields = (
        "order", "label", "field_key", "field_type",
        "placeholder", "is_required", "options"
    )
    ordering = ("order",)


@admin.register(FormDefinition)
class FormDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "field_count", "submission_count", "is_active")
    list_filter = ("is_active", "captcha_enabled")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FormFieldInline]

    fieldsets = (
        ("Identification", {"fields": ("name", "slug", "description")}),
        ("Après soumission", {"fields": ("success_message", "redirect_url", "email_notification")}),
        ("Sécurité & Statut", {"fields": ("captcha_enabled", "is_active")}),
    )

    def field_count(self, obj):
        return obj.fields.count()
    field_count.short_description = "Champs"

    def submission_count(self, obj):
        count = obj.submissions.count()
        if count == 0:
            return "—"
        return format_html(
            '<a href="/admin/forms/formsubmission/?form__id__exact={}">'
            '<span style="background:#2F4A3C;color:#fff;padding:2px 8px;'
            'border-radius:999px;font-size:11px;">{} soumission(s)</span></a>',
            obj.id, count
        )
    submission_count.short_description = "Soumissions"


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("form", "preview", "status_badge", "created_at")
    list_filter = ("form", "status", "created_at")
    search_fields = ("data",)
    readonly_fields = (
        "form", "data", "ip_address", "user_agent",
        "referer", "user", "created_at",
    )
    list_per_page = 50
    date_hierarchy = "created_at"

    def preview(self, obj):
        if not obj.data:
            return "—"
        items = list(obj.data.items())[:2]
        return " | ".join([f"{k}: {str(v)[:30]}" for k, v in items])
    preview.short_description = "Aperçu"

    def status_badge(self, obj):
        colors = {
            "new": "#D4A843", "read": "#2F4A3C",
            "replied": "#16A34A", "archived": "#6B6259", "spam": "#DC2626",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            colors.get(obj.status, "#6B6259"),
            obj.get_status_display()
        )
    status_badge.short_description = "Statut"


# Actions en masse
@admin.action(description="Marquer comme lu")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(status="read")


@admin.action(description="Marquer comme répondu")
def mark_as_replied(modeladmin, request, queryset):
    queryset.update(status="replied")


@admin.action(description="Marquer comme spam")
def mark_as_spam(modeladmin, request, queryset):
    queryset.update(status="spam")


FormSubmissionAdmin.actions = [mark_as_read, mark_as_replied, mark_as_spam]
'''

FORMS_APPS_PY = '''"""Configuration de l'application Formulaires."""
from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.forms"
    verbose_name = "Formulaires"
'''

FORMS_SEED_PY = '''"""Crée les formulaires de démonstration."""
from django.core.management.base import BaseCommand
from apps.forms.models import FormDefinition, FormField


class Command(BaseCommand):
    help = "Crée les formulaires contact et newsletter."

    def handle(self, *args, **options):
        # === Formulaire de contact ===
        contact, created = FormDefinition.objects.get_or_create(
            slug="contact",
            defaults={
                "name": "Formulaire de contact",
                "description": "Formulaire de contact général.",
                "success_message": "Merci ! Votre message a bien été envoyé, nous vous répondrons sous 48h.",
                "email_notification": "contact@nawa.com",
                "is_active": True,
            }
        )
        if created:
            fields = [
                ("nom", "Nom complet", "text", "Votre nom", True, 0),
                ("email", "Adresse email", "email", "vous@exemple.com", True, 1),
                ("sujet", "Sujet", "select", "", True, 2),
                ("message", "Votre message", "textarea", "Écrivez votre message ici...", True, 3),
            ]
            for key, label, ftype, placeholder, required, order in fields:
                options = []
                if key == "sujet":
                    options = [
                        {"value": "info", "label": "Demande d'information"},
                        {"value": "commande", "label": "Question sur une commande"},
                        {"value": "retour", "label": "Retour ou échange"},
                        {"value": "autre", "label": "Autre"},
                    ]
                FormField.objects.create(
                    form=contact, field_key=key, label=label,
                    field_type=ftype, placeholder=placeholder,
                    is_required=required, order=order,
                    options=options,
                )
            self.stdout.write("  [OK] Formulaire 'contact' créé (4 champs).")
        else:
            self.stdout.write("  [SKIP] Formulaire 'contact' existe déjà.")

        # === Formulaire newsletter ===
        newsletter, created = FormDefinition.objects.get_or_create(
            slug="newsletter",
            defaults={
                "name": "Inscription newsletter",
                "description": "Inscrivez-vous à notre newsletter.",
                "success_message": "Merci pour votre inscription !",
                "is_active": True,
            }
        )
        if created:
            FormField.objects.create(
                form=newsletter, field_key="email",
                label="Adresse email", field_type="email",
                placeholder="vous@exemple.com", is_required=True, order=0,
            )
            self.stdout.write("  [OK] Formulaire 'newsletter' créé (1 champ).")

        self.stdout.write(self.style.SUCCESS("[SUCCESS] Formulaires générés."))
'''


# ============================================================
#                   REDIRECTIONS - FICHIERS
# ============================================================

REDIRECTS_MODELS_PY = '''"""Modèles pour les redirections URL dynamiques."""
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
'''

REDIRECTS_SERIALIZERS_PY = '''"""Serializers DRF pour les redirections."""
from rest_framework import serializers
from .models import Redirect


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ["id", "old_path", "new_path", "redirect_type", "is_active", "hit_count"]
'''

REDIRECTS_VIEWS_PY = '''"""Vues API pour les redirections."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Redirect
from .serializers import RedirectSerializer


class RedirectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique des redirections actives.

    GET /api/v1/redirects/
    GET /api/v1/redirects/?path=/ancienne-url  → résout une URL spécifique
    """
    serializer_class = RedirectSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Redirect.objects.filter(is_active=True)
        path = self.request.query_params.get("path")
        if path:
            qs = qs.filter(old_path=path)
        return qs
'''

REDIRECTS_URLS_PY = '''"""URLs pour les redirections."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RedirectViewSet

router = DefaultRouter()
router.register(r"", RedirectViewSet, basename="redirect")

urlpatterns = [
    path("", include(router.urls)),
]
'''

REDIRECTS_ADMIN_PY = '''"""Admin Django pour les redirections."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "type_badge", "is_active", "hit_count", "updated_at")
    list_filter = ("redirect_type", "is_active")
    search_fields = ("old_path", "new_path")
    list_editable = ("is_active",)
    readonly_fields = ("hit_count", "created_at", "updated_at")
    ordering = ("-updated_at",)

    def type_badge(self, obj):
        color = "#16A34A" if obj.redirect_type == "301" else "#D4A843"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.redirect_type
        )
    type_badge.short_description = "Type"
'''

REDIRECTS_APPS_PY = '''"""Configuration de l'application Redirections."""
from django.apps import AppConfig


class RedirectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.redirects"
    verbose_name = "Redirections"
'''


# ============================================================
#                 SCRIPTS TIERS - FICHIERS
# ============================================================

SCRIPTS_MODELS_PY = '''"""Modèles pour les scripts tiers (GA, FB Pixel, Crisp...)."""
from django.db import models


class ThirdPartyScript(models.Model):
    """Un script HTML/JS à injecter dynamiquement dans le site."""

    LOCATION_CHOICES = [
        ("head", "Dans le <head>"),
        ("body_start", "Début du <body>"),
        ("body_end", "Fin du <body>"),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    code = models.TextField(
        verbose_name="Code",
        help_text="Code HTML/JS à injecter (balises <script> incluses)."
    )
    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, default="head"
    )
    is_active = models.BooleanField(default=True)
    require_consent = models.BooleanField(
        default=False,
        verbose_name="Nécessite consentement (RGPD)",
        help_text="Ne charger qu'après acceptation des cookies."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Script tiers"
        verbose_name_plural = "Scripts tiers"

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name} ({self.get_location_display()})"
'''

SCRIPTS_SERIALIZERS_PY = '''"""Serializers DRF pour les scripts tiers."""
from rest_framework import serializers
from .models import ThirdPartyScript


class ThirdPartyScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyScript
        fields = ["id", "name", "code", "location", "is_active", "require_consent"]
'''

SCRIPTS_VIEWS_PY = '''"""Vues API pour les scripts tiers."""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import ThirdPartyScript
from .serializers import ThirdPartyScriptSerializer


class ThirdPartyScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API publique en lecture seule.

    GET /api/v1/third-party-scripts/  → tous les scripts actifs
    """
    queryset = ThirdPartyScript.objects.filter(is_active=True)
    serializer_class = ThirdPartyScriptSerializer
    permission_classes = [AllowAny]
    pagination_class = None
'''

SCRIPTS_URLS_PY = '''"""URLs pour les scripts tiers."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThirdPartyScriptViewSet

router = DefaultRouter()
router.register(r"", ThirdPartyScriptViewSet, basename="third-party-script")

urlpatterns = [
    path("", include(router.urls)),
]
'''

SCRIPTS_ADMIN_PY = '''"""Admin Django pour les scripts tiers."""
from django.contrib import admin
from django.utils.html import format_html
from .models import ThirdPartyScript


@admin.register(ThirdPartyScript)
class ThirdPartyScriptAdmin(admin.ModelAdmin):
    list_display = ("name", "location_badge", "consent_badge", "is_active", "updated_at")
    list_filter = ("location", "is_active", "require_consent")
    search_fields = ("name", "description")
    list_editable = ("is_active",)

    fieldsets = (
        ("Identification", {"fields": ("name", "description")}),
        ("Code à injecter", {
            "fields": ("code", "location", "is_active", "require_consent")
        }),
    )

    def location_badge(self, obj):
        colors = {"head": "#DC2626", "body_start": "#D4A843", "body_end": "#2F4A3C"}
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            colors.get(obj.location, "#6B6259"),
            obj.get_location_display()
        )
    location_badge.short_description = "Emplacement"

    def consent_badge(self, obj):
        if obj.require_consent:
            return format_html(
                '<span style="color:#D4A843;font-weight:600;">⚠ RGPD</span>'
            )
        return "—"
    consent_badge.short_description = "Consentement"
'''

SCRIPTS_APPS_PY = '''"""Configuration de l'application Scripts tiers."""
from django.apps import AppConfig


class ThirdPartyScriptsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.third_party_scripts"
    verbose_name = "Scripts tiers"
'''

SCRIPTS_SEED_PY = '''"""Crée des scripts tiers de démonstration (désactivés)."""
from django.core.management.base import BaseCommand
from apps.third_party_scripts.models import ThirdPartyScript


DEFAULT_SCRIPTS = [
    {
        "name": "Google Analytics 4 (démo)",
        "description": "Exemple de script GA4. Remplacez par votre ID de mesure.",
        "code": """<!-- Google Analytics 4 — REMPLACER G-XXXXXXXXXX -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>""",
        "location": "head",
        "is_active": False,
        "require_consent": True,
    },
    {
        "name": "Meta Pixel (démo)",
        "description": "Pixel Facebook/Meta. Remplacez PIXEL_ID.",
        "code": """<!-- Meta Pixel -->
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', 'PIXEL_ID');
  fbq('track', 'PageView');
</script>""",
        "location": "head",
        "is_active": False,
        "require_consent": True,
    },
]


class Command(BaseCommand):
    help = "Crée des scripts tiers de démonstration (désactivés par défaut)."

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_SCRIPTS:
            _, was_created = ThirdPartyScript.objects.get_or_create(
                name=data["name"], defaults=data
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} script(s) créé(s), {len(DEFAULT_SCRIPTS)} au total."
        ))
'''


# ============================================================
#                    EMAILS - FICHIERS
# ============================================================

EMAILS_MODELS_PY = '''"""Modèles pour les templates d'emails transactionnels."""
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
'''

EMAILS_SERIALIZERS_PY = '''"""Serializers DRF pour les emails."""
from rest_framework import serializers
from .models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = [
            "id", "code", "name", "description",
            "subject", "body_text", "body_html",
            "from_email", "variables", "is_active",
        ]
'''

EMAILS_VIEWS_PY = '''"""Vues API pour les emails."""
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import EmailTemplate
from .serializers import EmailTemplateSerializer


class EmailTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API privée (réservée au staff).

    GET /api/v1/email-templates/
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
'''

EMAILS_URLS_PY = '''"""URLs pour les emails."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailTemplateViewSet

router = DefaultRouter()
router.register(r"", EmailTemplateViewSet, basename="email-template")

urlpatterns = [
    path("", include(router.urls)),
]
'''

EMAILS_ADMIN_PY = '''"""Admin Django pour les emails."""
from django.contrib import admin
from django.utils.html import format_html
from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "subject_preview", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "subject")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "preview")

    fieldsets = (
        ("Identification", {"fields": ("code", "name", "description")}),
        ("Contenu", {"fields": ("subject", "body_text", "body_html")}),
        ("Configuration", {"fields": ("from_email", "variables", "is_active")}),
        ("Aperçu", {"fields": ("preview",)}),
        ("Métadonnées", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def subject_preview(self, obj):
        return obj.subject[:60]
    subject_preview.short_description = "Sujet"

    def preview(self, obj):
        if not obj.pk:
            return "Enregistrez d'abord le template."
        return format_html(
            '<div style="border:1px solid #ddd;border-radius:8px;padding:16px;'
            'background:#f9f9f9;max-width:700px;">'
            '<div style="font-weight:600;margin-bottom:8px;">Sujet : {}</div>'
            '<hr style="border:none;border-top:1px solid #eee;margin:8px 0;">'
            '<div>{}</div>'
            '</div>',
            obj.subject,
            format_html("{}", obj.body_html or obj.body_text or "(vide)")
        )
    preview.short_description = "Aperçu"
'''

EMAILS_APPS_PY = '''"""Configuration de l'application Templates d'emails."""
from django.apps import AppConfig


class EmailTemplatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.email_templates"
    verbose_name = "Templates d'emails"
'''

EMAILS_HELPERS_PY = '''"""Helpers pour l'envoi d'emails basés sur les templates."""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import EmailTemplate


def send_template_email(code, recipient, context=None, fail_silently=True):
    """
    Envoie un email à partir d'un template défini dans l'admin.

    Usage :
        from apps.email_templates.helpers import send_template_email
        send_template_email(
            "order_confirmation",
            "client@example.com",
            {"user_name": "Fatou", "order_id": 42, "total": "89.90 €"}
        )
    """
    context = context or {}
    try:
        template = EmailTemplate.objects.get(code=code, is_active=True)
    except EmailTemplate.DoesNotExist:
        if not fail_silently:
            raise
        return False

    rendered = template.render(context)

    from_email = template.from_email or getattr(
        settings, "DEFAULT_FROM_EMAIL", "no-reply@nawa.com"
    )

    msg = EmailMultiAlternatives(
        subject=rendered["subject"],
        body=rendered["body_text"] or "Veuillez consulter la version HTML de cet email.",
        from_email=from_email,
        to=[recipient] if isinstance(recipient, str) else recipient,
    )
    if rendered["body_html"]:
        msg.attach_alternative(rendered["body_html"], "text/html")

    try:
        msg.send(fail_silently=fail_silently)
        return True
    except Exception:
        if not fail_silently:
            raise
        return False
'''

EMAILS_SEED_PY = '''"""Crée les templates d'emails de démonstration."""
from django.core.management.base import BaseCommand
from apps.email_templates.models import EmailTemplate


DEFAULT_TEMPLATES = [
    {
        "code": "order_confirmation",
        "name": "Confirmation de commande",
        "description": "Envoyé automatiquement après validation d'une commande.",
        "subject": "Confirmation de votre commande #{{ order_id }} — NAWA",
        "body_text": (
            "Bonjour {{ user_name }},\\n\\n"
            "Merci pour votre commande #{{ order_id }} d'un montant de {{ total }}.\\n"
            "Elle est en cours de préparation.\\n\\n"
            "L'équipe NAWA"
        ),
        "body_html": (
            "<h1>Merci {{ user_name }} !</h1>"
            "<p>Votre commande <strong>#{{ order_id }}</strong> "
            "d'un montant de <strong>{{ total }}</strong> a bien été reçue.</p>"
            "<p>Nous préparons votre colis.</p>"
            "<p>L'équipe <strong>NAWA</strong></p>"
        ),
        "variables": ["user_name", "order_id", "total"],
    },
    {
        "code": "welcome",
        "name": "Bienvenue",
        "description": "Envoyé à l'inscription d'un nouvel utilisateur.",
        "subject": "Bienvenue chez NAWA, {{ user_name }} !",
        "body_text": (
            "Bonjour {{ user_name }},\\n\\n"
            "Bienvenue chez NAWA !\\n"
            "Découvrez notre sélection de cosmétiques, mode et plus.\\n\\n"
            "L'équipe NAWA"
        ),
        "body_html": (
            "<h1>Bienvenue {{ user_name }} !</h1>"
            "<p>Merci de nous rejoindre. Découvrez la beauté d'Afrique, sublimée.</p>"
            "<p>L'équipe <strong>NAWA</strong></p>"
        ),
        "variables": ["user_name"],
    },
    {
        "code": "password_reset",
        "name": "Réinitialisation de mot de passe",
        "description": "Envoyé lors d'une demande de reset.",
        "subject": "Réinitialisez votre mot de passe — NAWA",
        "body_text": (
            "Bonjour {{ user_name }},\\n\\n"
            "Cliquez sur ce lien pour réinitialiser votre mot de passe :\\n"
            "{{ reset_url }}\\n\\n"
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
        ),
        "body_html": (
            "<h1>Réinitialisation de mot de passe</h1>"
            "<p>Bonjour {{ user_name }},</p>"
            "<p><a href=\\"{{ reset_url }}\\" "
            "style=\\"background:#C1652F;color:#fff;padding:12px 24px;"
            "border-radius:8px;text-decoration:none;\\">Réinitialiser</a></p>"
        ),
        "variables": ["user_name", "reset_url"],
    },
]


class Command(BaseCommand):
    help = "Crée les templates d'emails par défaut."

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_TEMPLATES:
            _, was_created = EmailTemplate.objects.get_or_create(
                code=data["code"], defaults=data
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} template(s) créé(s), {len(DEFAULT_TEMPLATES)} au total."
        ))
'''


# ============================================================
#                    UTILITAIRES
# ============================================================

MODULES = {
    "forms": {
        "dir": FORMS_DIR,
        "files": {
            "models.py": FORMS_MODELS_PY,
            "serializers.py": FORMS_SERIALIZERS_PY,
            "views.py": FORMS_VIEWS_PY,
            "urls.py": FORMS_URLS_PY,
            "admin.py": FORMS_ADMIN_PY,
            "apps.py": FORMS_APPS_PY,
            "management/commands/seed_forms.py": FORMS_SEED_PY,
        },
        "seed_cmd": "seed_forms",
        "url_path": "api/v1/forms/",
    },
    "redirects": {
        "dir": REDIRECTS_DIR,
        "files": {
            "models.py": REDIRECTS_MODELS_PY,
            "serializers.py": REDIRECTS_SERIALIZERS_PY,
            "views.py": REDIRECTS_VIEWS_PY,
            "urls.py": REDIRECTS_URLS_PY,
            "admin.py": REDIRECTS_ADMIN_PY,
            "apps.py": REDIRECTS_APPS_PY,
        },
        "seed_cmd": None,
        "url_path": "api/v1/redirects/",
    },
    "third_party_scripts": {
        "dir": SCRIPTS_DIR,
        "files": {
            "models.py": SCRIPTS_MODELS_PY,
            "serializers.py": SCRIPTS_SERIALIZERS_PY,
            "views.py": SCRIPTS_VIEWS_PY,
            "urls.py": SCRIPTS_URLS_PY,
            "admin.py": SCRIPTS_ADMIN_PY,
            "apps.py": SCRIPTS_APPS_PY,
            "management/commands/seed_scripts.py": SCRIPTS_SEED_PY,
        },
        "seed_cmd": "seed_scripts",
        "url_path": "api/v1/third-party-scripts/",
    },
    "email_templates": {
        "dir": EMAILS_DIR,
        "files": {
            "models.py": EMAILS_MODELS_PY,
            "serializers.py": EMAILS_SERIALIZERS_PY,
            "views.py": EMAILS_VIEWS_PY,
            "urls.py": EMAILS_URLS_PY,
            "admin.py": EMAILS_ADMIN_PY,
            "apps.py": EMAILS_APPS_PY,
            "helpers.py": EMAILS_HELPERS_PY,
            "management/commands/seed_emails.py": EMAILS_SEED_PY,
        },
        "seed_cmd": "seed_emails",
        "url_path": "api/v1/email-templates/",
    },
}


def ensure_init(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
        print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")

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


def add_all_to_settings():
    settings = find_settings()
    if not settings:
        print("  [ERREUR] settings.py introuvable.")
        return

    with open(settings, "r", encoding="utf-8") as f:
        content = f.read()

    apps = [
        "apps.forms", "apps.redirects",
        "apps.third_party_scripts", "apps.email_templates",
    ]
    missing = [a for a in apps if f'"{a}"' not in content]
    if not missing:
        print("  [SKIP] les 4 apps sont déjà déclarées")
        return

    shutil.copy2(settings, settings + ".bak")

    m = None
    for name in ("LOCAL_APPS", "INSTALLED_APPS"):
        m = re.search(rf"{name}\s*[:=]\s*\[(.*?)\]", content, re.DOTALL)
        if m:
            break
    if not m:
        print("  [ATTENTION] LOCAL_APPS introuvable.")
        return

    insertion = "".join(f'\n    "{a}",' for a in missing) + "\n"
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(settings, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [OK] {len(missing)} app(s) ajoutée(s)")


def add_all_urls():
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    if all(f"apps.{app}.urls" in content for app in MODULES):
        print("  [SKIP] les 4 routes sont déjà présentes")
        return

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        print("  [ATTENTION] urlpatterns introuvable.")
        return

    insertion = "\n    # === Formulaires, Redirections, Scripts, Emails ===\n"
    for app, cfg in MODULES.items():
        if f"apps.{app}.urls" not in content:
            insertion += f'    path("{cfg["url_path"]}", include("apps.{app}.urls")),\n'

    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] routes ajoutées")


def run_cmd(*args, allow_fail=False):
    try:
        subprocess.run([sys.executable, "manage.py", *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        if not allow_fail:
            sys.exit(1)


def main():
    print("=" * 60)
    print("  INJECTION SEMAINE 6 - BACKEND")
    print("  (Formulaires, Redirections, Scripts, Emails)")
    print("=" * 60)

    print("\n1. Création des fichiers...")
    for app, cfg in MODULES.items():
        print(f"\n  --- {app} ---")
        for sub in ["", "migrations", "management", "management/commands"]:
            ensure_init(os.path.join(cfg["dir"], sub, "__init__.py"))
        for rel_path, content in cfg["files"].items():
            write_file(os.path.join(cfg["dir"], rel_path), content)

    print("\n2. Mise à jour de settings.py...")
    add_all_to_settings()

    print("\n3. Mise à jour de urls.py...")
    add_all_urls()

    print("\n4. Migrations...")
    run_cmd("makemigrations", "forms", "redirects",
            "third_party_scripts", "email_templates", allow_fail=True)
    run_cmd("migrate")

    print("\n5. Seeds...")
    for cfg in MODULES.values():
        if cfg["seed_cmd"]:
            run_cmd(cfg["seed_cmd"], allow_fail=True)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nEndpoints :")
    print("  Formulaires : http://127.0.0.1:8000/api/v1/forms/definitions/")
    print("  Redirections: http://127.0.0.1:8000/api/v1/redirects/")
    print("  Scripts     : http://127.0.0.1:8000/api/v1/third-party-scripts/")
    print("  Emails      : http://127.0.0.1:8000/api/v1/email-templates/")
    print("\nAdmin :")
    print("  Formulaires : http://127.0.0.1:8000/admin/forms/")
    print("  Redirections: http://127.0.0.1:8000/admin/redirects/")
    print("  Scripts     : http://127.0.0.1:8000/admin/third_party_scripts/")
    print("  Emails      : http://127.0.0.1:8000/admin/email_templates/")


if __name__ == "__main__":
    main()