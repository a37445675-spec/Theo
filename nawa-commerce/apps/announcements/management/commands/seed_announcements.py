"""Crée des annonces de démonstration."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.announcements.models import Announcement


class Command(BaseCommand):
    help = "Crée des annonces de démonstration."

    def handle(self, *args, **options):
        if Announcement.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Des annonces existent déjà. Étape ignorée."
            ))
            return

        now = timezone.now()

        Announcement.objects.create(
            message="🎉 Livraison offerte dès 49€ d'achat !",
            link="/boutique/cosmetiques",
            link_label="Découvrir",
            background_color="#C1652F",
            text_color="#FFFFFF",
            position="top_bar",
            target_audience="all",
            is_active=True,
            order=0,
        )

        Announcement.objects.create(
            message="✨ Nouvelle collection Wax disponible",
            link="/boutique/vetements",
            link_label="Voir la collection",
            background_color="#2F4A3C",
            text_color="#F7F0E4",
            position="top_bar",
            target_audience="all",
            is_active=True,
            order=1,
        )

        Announcement.objects.create(
            message="Bienvenue sur NAWA ! Profitez de -10% sur votre première commande.",
            link="/inscription",
            link_label="Créer un compte",
            background_color="#D4A843",
            text_color="#221B15",
            position="popup",
            target_audience="anonymous",
            is_active=True,
            order=0,
            starts_at=now,
            ends_at=now + timedelta(days=30),
        )

        self.stdout.write(self.style.SUCCESS(
            "[OK] 3 annonces de démonstration créées."
        ))
