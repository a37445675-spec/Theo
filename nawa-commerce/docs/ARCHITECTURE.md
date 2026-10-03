# Architecture — NAWA Commerce

## 1. Le catalogue EAV multi-verticales (`apps.catalog`)

C'est le cœur du système, traité avec la profondeur maximale (modèles,
validation double (modèle + serializer), admin, filtrage dynamique, tests).

```
AttributeDefinition   — un attribut réutilisable (code, type, choix, unité)
AttributeSet          — regroupe des AttributeDefinition pour une verticale
AttributeSetItem       — table de liaison (obligatoire ou non, ordre)
Category               — arbre parent/enfant, pointe vers un AttributeSet
                          (héritage simple si non défini directement)
Brand                  — marque ou coopérative/productrice
Product                — champs communs + `attributes` (JSONField validé)
ProductVariant          — variantes (taille+couleur, pointure...) avec
                          stock/prix propres
ProductImage            — avec width/height stockés (anti-CLS)
```

**Pourquoi ça marche sans migration** : ajouter une verticale ("Chaussures")
consiste à créer des `AttributeDefinition`, un `AttributeSet`, et une
`Category` qui pointe dessus — aucune nouvelle table, aucune colonne. La
validation (`apps/catalog/validators.py::validate_attributes_against_set`)
est appelée à la fois par `Product.clean()` (admin, scripts, shell) et par
les serializers DRF (API), donc jamais contournable côté client.

Le filtrage dynamique (`apps/catalog/filters.py::DynamicAttributeFilterBackend`)
lit les `AttributeDefinition` de la catégorie demandée et construit les
lookups JSONField à la volée — un seul endpoint sert toutes les verticales.

## 2. Matrice de profondeur d'implémentation

Un projet de cette ampleur (23 apps, theme builder, B2B, POS, intégrations)
représente normalement plusieurs mois-personnes en production. Voici,
honnêtement, ce qui a été livré à quelle profondeur :

### Profondeur complète (modèles + validation + admin + serializers + vues + urls + tests)
`catalog` (EAV — la brique explicitement centrale), `accounts` (rôles via
Groups), `cart`, `checkout`, `orders`, `payments` (Stripe réel si clé
fournie, sinon simulation déterministe), `promotions`, `cms` (Theme Builder
headless complet : PageTemplate/PageBlock/GlobalDesignSystem/DynamicTag/SiteKit).

### Profondeur solide (modèles + admin + serializers + vues, logique de service réelle)
`billing` (génération de facture, échéance B2B), `loyalty`, `subscriptions`
(tâche Celery de réassort), `shipping` (interface `CarrierGateway` + 2
implémentations déterministes DHL/Colissimo), `blog`, `seo`.

### Interfaces d'extension documentées (modèles + point d'entrée de service au contrat stable, implémentation stub explicite)
`marketing` (webhooks sortants réels via Celery + connecteur emailing en
stub logué), `reporting` (agrégations Django ORM réelles sur données de
prod), `observability` (middleware + EventLog réels), `integration`
(connecteurs CRM/ERP en stub logué — le contrat `sync_customer_to_crm(connector, customer)`
est stable pour brancher un vrai SDK), `platform_settings`, `pos` (vente
magasin réelle, réutilise `orders.services.create_order_workflow`), `b2b`
(résolution de prix réelle), `bookings` (réservation avec contrôle de
capacité réel).

Cette transparence est volontaire : un stub explicite et documenté vaut
mieux qu'une fausse promesse de complétude qu'un audit découvrirait plus
tard.

## 3. Services de domaine (DDD léger)

```python
apps.orders.services.create_order_workflow(cart, shipping_address, ...)
apps.checkout.services.checkout_cart(cart, ...)
apps.billing.services.generate_invoice_for_order(order)
apps.payments.services.create_payment_intent(order)
apps.promotions.services.apply_discounts_to_cart(order, coupon)
apps.loyalty.services.apply_points(customer, order)
apps.reporting.services.generate_sales_report(date_from, date_to)
apps.core.tax.calculate_tax(order)                      # moteur fiscal dynamique
apps.shipping.services.get_gateway(carrier_code)          # abstraction transporteur
apps.b2b.services.get_price_for_customer(product, customer, quantity)
```

## 4. Rôles & permissions

Implémentés via `django.contrib.auth.models.Group` (pas un champ `role`
figé — un utilisateur peut cumuler plusieurs rôles) : `customer`,
`shop_manager`, `administrator`, `vendor`. Voir
`apps/core/permissions.py::IsShopManagerOrAdmin` pour la permission DRF
correspondante, appliquée sur les endpoints de gestion (produits,
commandes, coupons, rapports).

## 5. Multicanal (online + POS)

`Order.sales_channel` (`online` / `pos` / `marketplace`) permet un
historique unifié par client. `apps.pos.views.POSSaleView` réutilise
exactement `orders.services.create_order_workflow` — aucune divergence de
logique de stock entre vente en ligne et vente en magasin.

## 6. Sécurité & observabilité

- JWT (djangorestframework-simplejwt), rotation des refresh tokens.
- Enveloppe d'erreur uniforme (`apps/core/exceptions.py`).
- `RequestLogMiddleware` journalise les requêtes lentes (>1s) et les 5xx
  dans `EventLog`.
- Webhook Stripe vérifié par signature (`STRIPE_WEBHOOK_SECRET`) avant tout
  traitement.
