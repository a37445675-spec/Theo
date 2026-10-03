#!/bin/sh
set -e

echo "🚀 Démarrage du backend NAWA Commerce..."

# Attendre la base de données
echo "⏳ Attente de PostgreSQL..."
until python -c "import psycopg2; psycopg2.connect(dbname='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD', host='$DB_HOST', port='$DB_PORT')" 2>/dev/null; do
  echo "  PostgreSQL n'est pas encore prêt..."
  sleep 2
done
echo "✅ PostgreSQL prêt"

# Migrations
echo "📦 Application des migrations..."
python manage.py migrate --noinput

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Créer un superuser si premier démarrage
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "👤 Création du superuser..."
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser créé')
else:
    print('Superuser existe déjà')
"
fi

# Lancer la commande
exec "$@"
