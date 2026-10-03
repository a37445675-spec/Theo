"""Crée des étiquettes de démonstration pour la médiathèque."""
from django.core.management.base import BaseCommand
from apps.media_library.models import MediaTag


DEFAULT_TAGS = [
    ("Produits", "#C1652F"),
    ("Bannières", "#2F4A3C"),
    ("Blog", "#D4A843"),
    ("Avatars", "#6B6259"),
    ("Logos", "#221B15"),
    ("Lifestyle", "#8A4B26"),
    ("Cosmétiques", "#DC2626"),
    ("Mode", "#1E40AF"),
    ("Maison", "#16A34A"),
    ("Promos", "#F59E0B"),
]


class Command(BaseCommand):
    help = "Crée les étiquettes par défaut de la médiathèque."

    def handle(self, *args, **options):
        created = 0
        for name, color in DEFAULT_TAGS:
            _, was_created = MediaTag.objects.get_or_create(
                name=name, defaults={"color": color}
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} nouvelle(s) étiquette(s) créée(s), "
            f"{len(DEFAULT_TAGS)} au total."
        ))
