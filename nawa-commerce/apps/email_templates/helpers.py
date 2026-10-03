"""Helpers pour l'envoi d'emails basés sur les templates."""
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
