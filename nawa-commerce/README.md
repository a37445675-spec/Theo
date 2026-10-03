# NAWA Commerce — Backend Django

Plateforme e-commerce multi-verticales : cosmétiques naturels, vêtements,
chaussures, électroménager, et toute catégorie future — sur un **catalogue à
attributs dynamiques (EAV léger via JSONField Postgres)** ne nécessitant
aucune migration de schéma pour ajouter une nouvelle verticale.

## Démarrage rapide

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # configurer DB_*, STRIPE_*, etc.
createdb nawa_commerce             # PostgreSQL requis (JSONField + GIN index)
python manage.py migrate
python manage.py seed_nawa_demo    # données de démonstration multi-verticales
python manage.py runserver
```

- Admin : `/admin/` — superutilisateur créé par le seed : `admin` / `ChangeMoi123!`
- Documentation API (Swagger) : `/api/docs/`
- Schéma OpenAPI brut : `/api/schema/`

Celery (factures PDF, webhooks, emails, réassorts d'abonnement) :

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Documents

- `docs/ARCHITECTURE.md` — architecture détaillée, catalogue EAV, et **matrice
  de profondeur d'implémentation par domaine** (ce qui est complet et testé
  vs. les interfaces d'extension prêtes à brancher).
- `docs/FRONTEND_INTEGRATION.md` — comment un frontend ou un futur builder
  visuel consomme les templates, le design system, les dynamic tags et les
  widgets e-commerce exposés par `apps.cms`.

## Vérification rapide du catalogue EAV

```bash
python manage.py test apps.catalog
```

Couvre les trois scénarios explicitement requis : rejet d'un attribut hors
verticale (ex. 'voltage' sur un vêtement), filtrage dynamique par attribut,
et ajout d'une nouvelle catégorie/verticale sans migration.
