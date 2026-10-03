"""Crée les feature flags par défaut de NAWA."""
from django.core.management.base import BaseCommand
from apps.feature_flags.models import FeatureFlag


DEFAULT_FLAGS = [
    # (code, name, description, is_enabled, target_audience)
    ("wishlist", "Liste de souhaits",
     "Permet aux clients d'ajouter des produits à une liste de souhaits.", True, "authenticated"),
    ("reviews", "Avis clients",
     "Affiche les avis et notes sur les fiches produit.", True, "all"),
    ("header_search", "Recherche dans l'en-tête",
     "Affiche une barre de recherche dans le header.", True, "all"),
    ("guest_checkout", "Commande sans compte",
     "Autorise les visiteurs à commander sans créer de compte.", True, "all"),
    ("loyalty_program", "Programme de fidélité",
     "Active les points de fidélité et les récompenses.", True, "authenticated"),
    ("subscriptions", "Abonnements récurrents",
     "Active la vente par abonnement (livraison périodique).", False, "authenticated"),
    ("b2b_portal", "Portail B2B",
     "Active l'espace professionnel B2B avec tarifs dédiés.", False, "staff"),
    ("bookings", "Réservations",
     "Active la prise de rendez-vous pour les services.", False, "all"),
    ("pos_mode", "Mode Point de Vente",
     "Active l'interface de caisse pour les boutiques physiques.", False, "staff"),
    ("dark_mode", "Mode sombre",
     "Permet aux utilisateurs de basculer en thème sombre.", False, "all"),
]


class Command(BaseCommand):
    help = "Crée les feature flags par défaut."

    def handle(self, *args, **options):
        created_count = 0
        for code, name, desc, enabled, audience in DEFAULT_FLAGS:
            obj, created = FeatureFlag.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "is_enabled": enabled,
                    "target_audience": audience,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created_count} nouveau(x) flag(s) créé(s), "
            f"{len(DEFAULT_FLAGS)} au total."
        ))
