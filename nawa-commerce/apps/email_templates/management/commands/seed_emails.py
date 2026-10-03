"""Crée les templates d'emails de démonstration."""
from django.core.management.base import BaseCommand
from apps.email_templates.models import EmailTemplate


DEFAULT_TEMPLATES = [
    {
        "code": "order_confirmation",
        "name": "Confirmation de commande",
        "description": "Envoyé automatiquement après validation d'une commande.",
        "subject": "Confirmation de votre commande #{{ order_id }} — NAWA",
        "body_text": (
            "Bonjour {{ user_name }},\n\n"
            "Merci pour votre commande #{{ order_id }} d'un montant de {{ total }}.\n"
            "Elle est en cours de préparation.\n\n"
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
            "Bonjour {{ user_name }},\n\n"
            "Bienvenue chez NAWA !\n"
            "Découvrez notre sélection de cosmétiques, mode et plus.\n\n"
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
            "Bonjour {{ user_name }},\n\n"
            "Cliquez sur ce lien pour réinitialiser votre mot de passe :\n"
            "{{ reset_url }}\n\n"
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
        ),
        "body_html": (
            "<h1>Réinitialisation de mot de passe</h1>"
            "<p>Bonjour {{ user_name }},</p>"
            "<p><a href=\"{{ reset_url }}\" "
            "style=\"background:#C1652F;color:#fff;padding:12px 24px;"
            "border-radius:8px;text-decoration:none;\">Réinitialiser</a></p>"
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
