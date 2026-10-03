import logging

from rest_framework.views import exception_handler

logger = logging.getLogger("nawa.errors")


class DomainError(Exception):
    def __init__(self, message, code="domain_error"):
        self.message = message
        self.code = code
        super().__init__(message)


def nawa_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, DomainError) and response is None:
        from rest_framework.response import Response

        return Response({"error": {"code": exc.code, "message": exc.message}}, status=400)

    if response is not None:
        response.data = {
            "error": {
                "code": getattr(exc, "default_code", "error"),
                "message": str(exc),
                "details": response.data,
            }
        }

    if response is None or response.status_code >= 500:
        logger.exception("Erreur non gérée", extra={"context": str(context.get("view"))})

    return response
