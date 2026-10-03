"""Crée les formulaires de démonstration."""
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
