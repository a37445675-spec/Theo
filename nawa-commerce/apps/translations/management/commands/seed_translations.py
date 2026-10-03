"""Crée les clés de traduction de base."""
from django.core.management.base import BaseCommand
from apps.translations.models import TranslationKey


DEFAULT_KEYS = [
    # (key, fr, en, context, description)
    ("common.loading", "Chargement…", "Loading…", "Global", ""),
    ("common.error", "Une erreur est survenue.", "An error occurred.", "Global", ""),
    ("common.retry", "Réessayer", "Try again", "Global", ""),
    ("common.close", "Fermer", "Close", "Global", ""),
    ("common.search", "Rechercher", "Search", "Global", ""),
    ("common.cancel", "Annuler", "Cancel", "Global", ""),
    ("common.save", "Enregistrer", "Save", "Global", ""),
    ("common.delete", "Supprimer", "Delete", "Global", ""),
    ("common.confirm", "Confirmer", "Confirm", "Global", ""),

    ("nav.shop", "Boutique", "Shop", "Navigation", ""),
    ("nav.journal", "Journal", "Blog", "Navigation", ""),
    ("nav.account", "Mon compte", "My account", "Navigation", ""),
    ("nav.cart", "Panier", "Cart", "Navigation", ""),

    ("cart.empty.title", "Votre panier est vide", "Your cart is empty", "Panier", ""),
    ("cart.empty.cta", "Découvrir la boutique", "Browse the shop", "Panier", ""),
    ("cart.checkout", "Passer commande", "Checkout", "Panier", ""),
    ("cart.subtotal", "Sous-total", "Subtotal", "Panier", ""),
    ("cart.shipping", "Livraison", "Shipping", "Panier", ""),
    ("cart.total", "Total", "Total", "Panier", ""),

    ("checkout.title", "Finaliser la commande", "Complete your order", "Commande", ""),
    ("checkout.payment", "Paiement", "Payment", "Commande", ""),
    ("checkout.address", "Adresse de livraison", "Shipping address", "Commande", ""),
    ("checkout.success", "Merci pour votre commande !", "Thank you for your order!", "Commande", ""),

    ("auth.login", "Connexion", "Sign in", "Authentification", ""),
    ("auth.register", "Créer un compte", "Sign up", "Authentification", ""),
    ("auth.logout", "Se déconnecter", "Sign out", "Authentification", ""),
    ("auth.email", "Adresse email", "Email address", "Authentification", ""),
    ("auth.password", "Mot de passe", "Password", "Authentification", ""),
    ("auth.forgot", "Mot de passe oublié ?", "Forgot password?", "Authentification", ""),

    ("product.add_to_cart", "Ajouter au panier", "Add to cart", "Produit", ""),
    ("product.out_of_stock", "Rupture de stock", "Out of stock", "Produit", ""),
    ("product.reviews", "Avis clients", "Customer reviews", "Produit", ""),
    ("product.description", "Description", "Description", "Produit", ""),
    ("product.shipping_info", "Livraison & retours", "Shipping & returns", "Produit", ""),

    ("footer.about", "À propos", "About", "Pied de page", ""),
    ("footer.contact", "Contact", "Contact", "Pied de page", ""),
    ("footer.legal", "Mentions légales", "Legal notice", "Pied de page", ""),
    ("footer.privacy", "Confidentialité", "Privacy", "Pied de page", ""),

    ("empty.no_results", "Aucun résultat", "No results", "États vides", ""),
    ("empty.no_orders", "Aucune commande pour le moment", "No orders yet", "États vides", ""),
    ("empty.no_products", "Aucun produit disponible", "No products available", "États vides", ""),
]


class Command(BaseCommand):
    help = "Crée les clés de traduction par défaut (FR/EN)."

    def handle(self, *args, **options):
        created_count = 0
        for key, fr, en, ctx, desc in DEFAULT_KEYS:
            obj, created = TranslationKey.objects.update_or_create(
                key=key,
                defaults={
                    "values": {"fr": fr, "en": en},
                    "context": ctx,
                    "description": desc,
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created_count} nouvelles clés créées, {len(DEFAULT_KEYS)} au total."
        ))
