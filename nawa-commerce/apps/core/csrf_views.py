"""Vue CSRF — pose le cookie pour les clients SPA."""
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET


@require_GET
@ensure_csrf_cookie
def csrf_bootstrap(request):
    """
    Endpoint appelé par le SPA au boot pour obtenir un token CSRF.
    Pose le cookie csrftoken ET retourne le token dans le JSON.
    """
    token = get_token(request)
    return JsonResponse({"csrfToken": token})