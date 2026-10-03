"""Crée les menus par défaut NAWA (Header + Footer)."""
from django.core.management.base import BaseCommand
from apps.navigation.models import Menu, MenuItem


class Command(BaseCommand):
    help = "Crée les menus Header et Footer par défaut."

    def handle(self, *args, **options):
        # ---- Menu Header ----
        header, created = Menu.objects.get_or_create(
            slug="header-main",
            defaults={
                "name": "Menu principal",
                "location": "header",
                "order": 0,
                "is_active": True,
            }
        )
        if created:
            self.stdout.write("  [OK] Menu 'header-main' créé.")
        else:
            self.stdout.write("  [SKIP] Menu 'header-main' existe déjà.")

        header_items = [
            # (label, url, order, visibility, badge_text, badge_color)
            ("Cosmétiques", "/boutique/cosmetiques", 0, "all", "", ""),
            ("Vêtements", "/boutique/vetements", 1, "all", "", ""),
            ("Chaussures", "/boutique/chaussures", 2, "all", "", ""),
            ("Électroménager", "/boutique/electromenager", 3, "all", "", ""),
            ("Journal", "/journal", 4, "all", "", ""),
            ("Gestion", "/gestion/commandes", 5, "staff", "Staff", "#2F4A3C"),
        ]
        for label, url, order, visibility, badge, color in header_items:
            MenuItem.objects.update_or_create(
                menu=header, label=label,
                defaults={
                    "url": url,
                    "order": order,
                    "is_visible": True,
                    "visibility": visibility,
                    "badge_text": badge,
                    "badge_color": color or "#C1652F",
                }
            )
        self.stdout.write(f"  [OK] {len(header_items)} items pour le Header.")

        # ---- Menu Footer ----
        footer, created = Menu.objects.get_or_create(
            slug="footer-main",
            defaults={
                "name": "Menu pied de page",
                "location": "footer",
                "order": 0,
                "is_active": True,
            }
        )
        if created:
            self.stdout.write("  [OK] Menu 'footer-main' créé.")

        footer_items = [
            ("À propos", "/a-propos", 0),
            ("Contact", "/contact", 1),
            ("CGV", "/cgv", 2),
            ("Mentions légales", "/mentions-legales", 3),
            ("Politique de confidentialité", "/confidentialite", 4),
            ("Retours & remboursements", "/retours", 5),
        ]
        for label, url, order in footer_items:
            MenuItem.objects.update_or_create(
                menu=footer, label=label,
                defaults={"url": url, "order": order, "is_visible": True, "visibility": "all"}
            )
        self.stdout.write(f"  [OK] {len(footer_items)} items pour le Footer.")
        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Menus de navigation générés."))
