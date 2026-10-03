# NAWA Shop Frontend

Frontend React (Vite) branché sur **nawa-commerce** — le backend Django à
catalogue multi-verticales (cosmétiques, vêtements, chaussures, électroménager).
Toutes les pages sont connectées à des appels API réels ; aucune n'est un
stub statique.

## Démarrage

```bash
npm install
cp .env.example .env
npm run dev
```

Le proxy Vite redirige `/api` et `/media` vers `http://localhost:8000` —
lancez le backend nawa-commerce avec `python manage.py seed_nawa_demo` au
préalable pour avoir des données à afficher.

## Différence clé avec les frontends précédents

**Toute l'API nawa-commerce répond en camelCase, uniformément** (contrairement
à un backend hybride Wagtail/Oscar) — voir `config/settings.py::REST_FRAMEWORK`
côté backend. `src/api/` ne fait donc aucune conversion snake_case↔camelCase.

## Pages livrées (20, toutes opérationnelles)

| Route | Page | Données |
|---|---|---|
| `/` | Accueil | Gabarit CMS (`apps.cms`) si défini par le seed, sinon repli par défaut |
| `/boutique/:categorySlug` | Boutique | Produits + filtres dynamiques selon l'AttributeSet de la catégorie |
| `/produit/:slug` | Fiche produit | Variantes, attributs par verticale, ajout panier |
| `/reservations/:slug` | Créneaux (produits `booking`) | Liste de créneaux + réservation |
| `/panier` | Panier | Lignes, quantités, suppression |
| `/commande` | Checkout | Adresse, code promo, création de commande |
| `/commande/confirmation/:id` | Confirmation | Récapitulatif, statut de paiement |
| `/journal`, `/journal/:slug` | Blog | Articles, catégories, commentaires |
| `/connexion`, `/inscription` | Auth | JWT (access/refresh, rotation automatique) |
| `/compte` | Profil | Édition, aperçu fidélité/commandes/abonnements |
| `/compte/commandes`, `/compte/commandes/:id` | Commandes | Historique + détail + suivi de statut |
| `/compte/adresses` | Adresses | Création/suppression |
| `/compte/fidelite` | Fidélité | Solde, palier, historique de points |
| `/compte/abonnements` | Abonnements | Fréquence, pause, suppression |
| `/compte/factures` | Factures | Liste + lien PDF si généré |
| `/gestion/commandes` | Back-office (Shop Manager) | Changement de statut des commandes |

## Point d'honnêteté — paiement en mode démo

Sans clé Stripe configurée côté backend, `create_payment_intent` renvoie une
intention **simulée** : la commande reste au statut "En attente de paiement"
jusqu'à réception d'un vrai webhook Stripe (`payment_intent.succeeded`). La
page de confirmation l'explique clairement plutôt que de simuler un succès —
en développement, faites basculer la commande via l'admin Django, ou
configurez `STRIPE_SECRET_KEY`/`STRIPE_WEBHOOK_SECRET` pour le flux réel.

## Structure

```
src/
├── api/          Un module par domaine (auth, catalog, cart, checkout, orders,
│                 billing, subscriptions, loyalty, promotions, shipping, blog, cms, bookings)
├── context/      AuthContext (JWT), CartContext
├── hooks/        useFetch (chargement/erreur générique), useReveal
├── components/
│   ├── blocks/    Dispatcher de blocs CMS (Theme Builder headless)
│   └── shop/       ProductCard, CategoryFilterSidebar (filtres 100% dynamiques)
└── pages/          20 pages, toutes branchées à l'API
```


## Design system v2 — UI / UX / CX

- **Typographie** : Segoe UI (pile système : Segoe UI → -apple-system →
  Roboto → Arial) pour tout le texte d'interface, Fraunces conservé pour les
  titres de marque — lisibilité native + identité visuelle.
- **Animations** : transition de page à chaque navigation, apparition en
  cascade des grilles produits/blog, zoom image au survol des cartes, effet
  ressort sur les boutons et les filtres actifs, badge panier animé, menu
  mobile avec fond assombri animé, accordéon FAQ fluide, spinners de
  chargement sur les CTA critiques (connexion, inscription, paiement, ajout
  panier) au lieu d'un texte "…" statique. Toutes les animations respectent
  `prefers-reduced-motion`.
- **CX** : `LoyaltyProgress` visualise la progression vers le palier de
  fidélité suivant (au lieu d'un simple nombre de points) ; `OrderStatusTimeline`
  transforme l'historique de statut en parcours visuel animé, réutilisé sur
  la confirmation de commande et le détail de commande.
- **Médiathèque** (`public/`) : icônes PWA multi-résolutions, écrans de
  démarrage iOS, images de repli par verticale, illustrations d'états
  vides/erreur, images de partage social — actifs réels, pas de remplissage.
