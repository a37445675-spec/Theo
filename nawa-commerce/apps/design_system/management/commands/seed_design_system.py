"""Crée un Design System par défaut."""
from django.core.management.base import BaseCommand
from apps.design_system.models import DesignSystem


class Command(BaseCommand):
    help = "Crée le Design System par défaut NAWA."

    def handle(self, *args, **options):
        if DesignSystem.objects.exists():
            self.stdout.write(self.style.WARNING("Un Design System existe déjà."))
            return

        DesignSystem.objects.create(
            name="NAWA Design System",
            is_active=True,
            color_primary="#C1652F",
            color_secondary="#2F4A3C",
            color_background="#F7F0E4",
            color_surface="#FFFFFF",
            color_text="#221B15",
            color_text_muted="#6B6259",
            color_accent="#D4A843",
            color_error="#DC2626",
            color_success="#16A34A",
            font_heading="Fraunces",
            font_body="Sora",
            font_size_base="16px",
            font_size_h1="3.5rem",
            font_size_h2="2.5rem",
            font_size_h3="1.75rem",
            line_height="1.6",
        )
        self.stdout.write(self.style.SUCCESS("[OK] Design System créé avec succès."))
