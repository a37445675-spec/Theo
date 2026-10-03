"""Vues API pour les formulaires."""
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
            body = f"Nouvelle soumission pour '{form.name}'\n\n"
            for key, value in submission.data.items():
                body += f"{key} : {value}\n"
            send_mail(
                subject=f"[NAWA] Nouveau formulaire — {form.name}",
                message=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nawa.com"),
                recipient_list=[form.email_notification],
                fail_silently=True,
            )
        except Exception:
            pass
