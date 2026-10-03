"""
Middleware de cache HTTP pour les endpoints publics.
Ajoute des headers Cache-Control aux réponses API publiques.
"""
import re
from django.utils.deprecation import MiddlewareMixin


class CacheControlMiddleware(MiddlewareMixin):
    """
    Ajoute des headers Cache-Control sur les réponses API.
    Différencie les endpoints publics (cacheables) des privés (non cacheables).
    """

    # Endpoints publics cacheables (regex, durée en secondes)
    PUBLIC_CACHE = [
        (r"^/api/v1/design-system/", 3600),         # 1 heure
        (r"^/api/v1/navigation/", 1800),            # 30 minutes
        (r"^/api/v1/translations/", 3600),          # 1 heure
        (r"^/api/v1/feature-flags/", 300),          # 5 minutes
        (r"^/api/v1/announcements/", 300),          # 5 minutes
        (r"^/api/v1/media-library/", 1800),         # 30 minutes
        (r"^/api/v1/catalog/categories/", 1800),    # 30 minutes
        (r"^/api/v1/catalog/products/", 300),       # 5 minutes
        (r"^/api/v1/blog/categories/", 1800),       # 30 minutes
        (r"^/api/v1/blog/tags/", 1800),             # 30 minutes
        (r"^/api/v1/blog/posts/", 300),             # 5 minutes
        (r"^/api/v1/seo/", 3600),                   # 1 heure
        (r"^/api/v1/redirects/", 3600),             # 1 heure
    ]

    # Endpoints jamais cacheables
    PRIVATE_ENDPOINTS = [
        r"^/api/v1/auth/",
        r"^/api/v1/cart/",
        r"^/api/v1/checkout/",
        r"^/api/v1/orders/",
        r"^/api/v1/accounts/",
        r"^/api/v1/cms/",
        r"^/api/v1/forms/",
        r"^/admin/",
    ]

    def process_response(self, request, response):
        path = request.path

        # Ne pas toucher aux endpoints privés
        for pattern in self.PRIVATE_ENDPOINTS:
            if re.match(pattern, path):
                response["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
                return response

        # Cache uniquement les GET réussis
        if request.method != "GET" or response.status_code >= 400:
            response["Cache-Control"] = "no-store"
            return response

        # Endpoints publics cacheables
        for pattern, duration in self.PUBLIC_CACHE:
            if re.match(pattern, path):
                response["Cache-Control"] = f"public, max-age={duration}, stale-while-revalidate={duration * 2}"
                response["Vary"] = "Accept, Accept-Language, Origin"
                return response

        # Par défaut : cache court
        response["Cache-Control"] = "public, max-age=60"
        return response
