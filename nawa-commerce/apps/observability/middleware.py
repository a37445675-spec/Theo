import time


class RequestLogMiddleware:
    """Journalise durée/statut de chaque requête API, remonte les requêtes lentes (>1s) et les erreurs 5xx."""

    SLOW_REQUEST_THRESHOLD_MS = 1000

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        if request.path.startswith("/api/") and (duration_ms > self.SLOW_REQUEST_THRESHOLD_MS or response.status_code >= 500):
            from .services import log_event

            log_event(
                event_type="slow_request" if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS else "server_error",
                message=f"{request.method} {request.path}",
                user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
                metadata={"method": request.method, "path": request.path},
                duration_ms=duration_ms, status_code=response.status_code,
            )
        return response
