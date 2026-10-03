"""Crée une page d'exemple avec des widgets de démo."""
from django.core.management.base import BaseCommand
from apps.cms.models import PageTemplate, Widget


class Command(BaseCommand):
    help = "Crée une page d'exemple avec des widgets variés."

    def handle(self, *args, **options):
        page, created = PageTemplate.objects.get_or_create(
            name="Page Builder Démo",
            defaults={"template_type": "home"}
        )
        if not created and page.widgets.exists():
            self.stdout.write(self.style.WARNING(
                "La page a déjà des widgets. Étape ignorée."
            ))
            return

        page.widgets.all().delete()

        # Section Hero
        hero = Widget.objects.create(
            page=page, widget_type="section",
            name="Section Hero", order=0,
            content={}, style={"padding": "80px 0", "background": "#F7F0E4"}
        )
        col_left = Widget.objects.create(
            page=page, parent=hero, widget_type="column",
            name="Colonne gauche", order=0,
            content={}, style={"width": "50%"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="heading",
            order=0,
            content={"text": "La beauté d'Afrique, sublimée.", "level": "h1"},
            style={"color": "#221B15", "marginBottom": "16px"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="text",
            order=1,
            content={"text": "Découvrez notre sélection de cosmétiques naturels, mode et maison."},
            style={"fontSize": "18px", "color": "#6B6259"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="button",
            order=2,
            content={"label": "Découvrir", "url": "/boutique/cosmetiques"},
            style={"backgroundColor": "#C1652F", "color": "#fff"}
        )
        col_right = Widget.objects.create(
            page=page, parent=hero, widget_type="column",
            name="Colonne droite", order=1,
            content={}, style={"width": "50%"}
        )
        Widget.objects.create(
            page=page, parent=col_right, widget_type="image",
            order=0,
            content={"src": "/fallbacks/hero-fallback.jpg", "alt": "Hero"},
            style={"borderRadius": "24px"}
        )

        self.stdout.write(self.style.SUCCESS(
            "[OK] Page 'Page Builder Démo' créée avec 6 widgets."
        ))
