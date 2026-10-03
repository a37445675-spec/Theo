# Intégration Front — comment consommer le Theme Builder headless

L'objectif de `apps.cms` n'est pas de recréer Elementor, mais d'exposer
toutes les données dont un frontend (ou un futur builder visuel) a besoin
pour offrir une expérience de type Theme Builder / WooCommerce Builder.

## 1. Récupérer le gabarit d'une page

```
GET /api/cms/templates/?context=single_product&category=electromenager
```

Le backend résout le gabarit le plus prioritaire dont les
`display_conditions` correspondent au contexte fourni (catégorie, rôle,
pays, langue...), et retourne ses blocs ordonnés :

```json
{
  "name": "Fiche produit standard",
  "template_type": "single_product",
  "blocks": [
    { "block_type": "product_single", "order": 0,
      "dynamic_content": { "title": "{{ product.title }}", "price": "{{ product.price }}" } }
  ]
}
```

Le frontend itère sur `blocks` et rend le composant React/Vue correspondant
à chaque `block_type` (`hero`, `product_grid`, `cart_widget`, `faq`...) —
exactement le mécanisme d'un dispatcher de blocs CMS headless.

## 2. Résoudre les dynamic tags

`dynamic_content` contient des placeholders (`{{ product.title }}`). Le
frontend les résout contre l'objet réel (produit, article, utilisateur,
commande) chargé par ailleurs via l'API catalogue/commandes. Le registre
`GET /api/cms/dynamic-tags/?context=product` liste tous les tags
disponibles pour un contexte — utile pour peupler un sélecteur dans un
futur éditeur visuel.

## 3. Appliquer le design system global

```
GET /api/design-system/
```

Retourne `global_colors`, `global_typography`, `global_components` —  à
injecter comme variables CSS/tokens de design au chargement de
l'application, indépendamment du type de page affichée.

## 4. Widgets e-commerce

Chaque `block_type` e-commerce consomme l'API existante, sans logique
dupliquée :

| block_type | Endpoint consommé |
|---|---|
| `product_single` / `product_grid` | `/api/catalog/products/` |
| `cart_widget` / `menu_cart` | `/api/cart/` |
| `checkout_widget` | `/api/checkout/` + `/api/payments/` |
| `my_account_widget` | `/api/auth/me/` + `/api/orders/` |
| `blog_list` | `/api/blog/posts/` |
| `form` | (voir formulaires de contact — à brancher sur un endpoint dédié) |

## 5. Kits de site (campagnes, saisons, pays)

```
POST /api/cms/site-kits/apply/{id}/
```

Active tous les `PageTemplate` d'un `SiteKit` et désactive les gabarits
concurrents du même type — permet de basculer toute une expérience de site
(page d'accueil, boutique, fiche produit) en un seul appel, pour une
campagne saisonnière par exemple.

## 6. SEO / SSR

`apps.seo.models.product_json_ld(product, request)` génère le JSON-LD
schema.org `Product`/`Offer` prêt à injecter côté SSR (Next.js `getServerSideProps`
ou équivalent) pour le rendu initial et l'indexation.
