"""
URLs racine — NAWA Commerce.

Toutes les APIs sont exposées sous /api/v1/<domaine>/, plus la documentation
OpenAPI (drf-spectacular) et l'admin Django.

Ordre important : les routes spécifiques (widgets, sous-ressources) doivent
être déclarées AVANT les routes génériques pour primer lors du routing.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.core.csrf_views import csrf_bootstrap


urlpatterns = [
    # ============================================================
    #  ADMIN DJANGO
    # ============================================================
    path("admin/", admin.site.urls),

    # === CSRF bootstrap ===
    path("api/v1/csrf/", csrf_bootstrap, name="csrf-bootstrap"),


    # ============================================================
    #  AUTHENTIFICATION (JWT)
    # ============================================================
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/v1/auth/", include("apps.accounts.urls")),

    # ============================================================
    #  DOMAINES MÉTIER
    # ============================================================
    path("api/v1/catalog/", include("apps.catalog.urls")),
    path("api/v1/cart/", include("apps.cart.urls")),
    path("api/v1/checkout/", include("apps.checkout.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/subscriptions/", include("apps.subscriptions.urls")),
    path("api/v1/loyalty/", include("apps.loyalty.urls")),
    path("api/v1/promotions/", include("apps.promotions.urls")),
    path("api/v1/shipping/", include("apps.shipping.urls")),
    path("api/v1/blog/", include("apps.blog.urls")),
    path("api/v1/reporting/", include("apps.reporting.urls")),
    path("api/v1/pos/", include("apps.pos.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),

    # ============================================================
    #  CMS HEADLESS — Ordre critique
    # ============================================================
    # Widget Builder EN PREMIER : ses routes (/widgets/, /reusable-sections/)
    # doivent primer sur le router général CMS.
    path("api/v1/cms/", include("apps.cms.widget_urls")),
    # CMS général : page-templates, blocks, etc.
    path("api/v1/cms/", include("apps.cms.urls")),

    # ============================================================
    #  MODULES CMS HEADLESS (Phases 1 à 7)
    # ============================================================
    # Design System (couleurs, typographies)
    path("api/v1/design-system/", include("apps.design_system.urls")),

    # Navigation (menus dynamiques)
    path("api/v1/navigation/", include("apps.navigation.urls")),

    # SEO & Traductions
    path("api/v1/seo/", include("apps.seo.urls")),
    path("api/v1/translations/", include("apps.translations.urls")),

    # Feature Flags & Annonces
    path("api/v1/feature-flags/", include("apps.feature_flags.urls")),
    path("api/v1/announcements/", include("apps.announcements.urls")),

    # Médiathèque
    path("api/v1/media-library/", include("apps.media_library.urls")),

    # Formulaires, Redirections, Scripts, Emails
    path("api/v1/forms/", include("apps.forms.urls")),
    path("api/v1/redirects/", include("apps.redirects.urls")),
    path("api/v1/third-party-scripts/", include("apps.third_party_scripts.urls")),
    path("api/v1/email-templates/", include("apps.email_templates.urls")),

    # ============================================================
    #  DOCUMENTATION API
    # ============================================================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


# ============================================================
#  FICHIERS MÉDIA (développement uniquement)
# ============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)