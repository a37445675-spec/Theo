"""
Phase 12.3 — Docker.
Crée Dockerfiles, docker-compose.yml, nginx.conf, .dockerignore.

Usage : python setup_docker.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "nawa-commerce")
FRONTEND_DIR = os.path.join(BASE_DIR, "nawa-shop-frontend")


# ============================================================
#              BACKEND DOCKERFILE
# ============================================================

BACKEND_DOCKERFILE = '''# ============================================================
#  NAWA Commerce — Backend Dockerfile
#  Python 3.11 + Django 5 + Gunicorn
# ============================================================
FROM python:3.11-slim AS builder

# Dépendances système pour build
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    libpq-dev \\
    libjpeg-dev \\
    zlib1g-dev \\
    libffi-dev \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements d'abord (cache Docker)
COPY requirements.txt .

# Installer dans un venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt && \\
    pip install --no-cache-dir gunicorn whitenoise


# ============================================================
#  IMAGE FINALE
# ============================================================
FROM python:3.11-slim

# Dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \\
    libpq-dev \\
    libjpeg-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copier le venv depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Utilisateur non-root
RUN useradd -m -u 1000 nawa
WORKDIR /app

# Copier le code
COPY --chown=nawa:nawa . .

# Créer les dossiers nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs && \\
    chown -R nawa:nawa /app/staticfiles /app/media /app/logs

USER nawa

# Variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    DJANGO_SETTINGS_MODULE=config.settings_production

# Port exposé
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/api/v1/design-system/active/ || exit 1

# Script de démarrage
COPY --chown=nawa:nawa docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
'''


BACKEND_ENTRYPOINT = '''#!/bin/sh
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
'''


# ============================================================
#              FRONTEND DOCKERFILE
# ============================================================

FRONTEND_DOCKERFILE = '''# ============================================================
#  NAWA Commerce — Frontend Dockerfile
#  Node 20 + Vite → Nginx
# ============================================================

# === ÉTAPE 1 : Build ===
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci --legacy-peer-deps

# Copier le code source
COPY . .

# Build de production
RUN npm run build


# === ÉTAPE 2 : Nginx ===
FROM nginx:alpine

# Copier la config Nginx
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx-frontend.conf /etc/nginx/conf.d/default.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\
    CMD wget -q -O /dev/null http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
'''


NGINX_FRONTEND = '''server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Compression Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/x-javascript
        application/json
        application/xml
        application/xml+rss
        image/svg+xml;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "public, max-age=0, must-revalidate";
    }

    # Assets statiques (cache 1 an)
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Proxy API vers le backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy admin
    location /admin/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy media
    location /media/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }

    # Proxy static
    location /static/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
'''


# ============================================================
#              DOCKER COMPOSE
# ============================================================

DOCKER_COMPOSE = '''# ============================================================
#  NAWA Commerce — Stack complète
#  Django + PostgreSQL + Redis + Nginx (frontend)
# ============================================================
version: "3.9"

services:
  # === PostgreSQL ===
  postgres:
    image: postgres:16-alpine
    container_name: nawa-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-nawa_commerce}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-Decembre2}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # === Redis ===
  redis:
    image: redis:7-alpine
    container_name: nawa-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # === Backend Django ===
  backend:
    build:
      context: ./nawa-commerce
      dockerfile: Dockerfile
    container_name: nawa-backend
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - ./nawa-commerce/.env.docker
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      REDIS_URL: redis://redis:6379/0
      USE_REDIS: "True"
      CREATE_SUPERUSER: "true"
    volumes:
      - ./nawa-commerce/media:/app/media
      - ./nawa-commerce/staticfiles:/app/staticfiles
      - ./nawa-commerce/logs:/app/logs
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/design-system/active/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # === Frontend Nginx ===
  frontend:
    build:
      context: ./nawa-shop-frontend
      dockerfile: Dockerfile
    container_name: nawa-frontend
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    ports:
      - "80:80"
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "/dev/null", "http://localhost/"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: nawa-network
'''


# ============================================================
#              ENV DOCKER
# ============================================================

ENV_DOCKER = '''# ============================================================
#  Variables d'environnement Docker
# ============================================================

SECRET_KEY=REMPLACEZ_PAR_VOTRE_CLE_SECRETE_DE_50_CARACTERES_MINIMUM
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend,nawa-backend

DB_NAME=nawa_commerce
DB_USER=postgres
DB_PASSWORD=Decembre2
DB_HOST=postgres
DB_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

USE_REDIS=True

FRONTEND_URL=http://localhost
CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:80
CSRF_TRUSTED_ORIGINS=http://localhost,http://localhost:80

SECURE_SSL_REDIRECT=False
ADMIN_URL=admin/

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=NAWA <no-reply@nawa.com>

CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@nawa.com
DJANGO_SUPERUSER_PASSWORD=ChangeMoi123!
'''


# ============================================================
#              DOCKERIGNORE
# ============================================================

BACKEND_DOCKERIGNORE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
.env
.env.production
.env.local

# IDE
.vscode/
.idea/
*.swp

# Tests
.coverage
htmlcov/
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore
'''

FRONTEND_DOCKERIGNORE = '''node_modules/
dist/
.vite/
.env
.env.production
.env.local
*.log
.git/
.gitignore
.vscode/
.idea/
coverage/
'''


DEPLOY_SCRIPT = '''# ============================================================
#  NAWA Commerce — Déploiement Docker
# ============================================================

Write-Host "🚀 Déploiement NAWA Commerce" -ForegroundColor Cyan
Write-Host ""

# Vérifier Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    Write-Host "→ Installez Docker Desktop : https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Build des images
Write-Host "🔨 Build des images Docker..." -ForegroundColor Cyan
docker compose build

# Démarrage
Write-Host ""
Write-Host "🚀 Démarrage des services..." -ForegroundColor Cyan
docker compose up -d

# Attendre
Write-Host ""
Write-Host "⏳ Attente du démarrage (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# État
Write-Host ""
Write-Host "📊 État des services :" -ForegroundColor Cyan
docker compose ps

# Logs backend
Write-Host ""
Write-Host "📋 Derniers logs backend :" -ForegroundColor Cyan
docker compose logs --tail=20 backend

Write-Host ""
Write-Host "✅ Déploiement terminé" -ForegroundColor Green
Write-Host ""
Write-Host "Accès :" -ForegroundColor Cyan
Write-Host "  Frontend : http://localhost"
Write-Host "  Backend  : http://localhost:8000"
Write-Host "  Admin    : http://localhost/admin/"
Write-Host ""
Write-Host "Commandes utiles :" -ForegroundColor Cyan
Write-Host "  docker compose logs -f backend    # Voir les logs"
Write-Host "  docker compose down               # Arrêter"
Write-Host "  docker compose restart backend    # Redémarrer"
'''


# ============================================================
#              FONCTIONS
# ============================================================

def write_file(path, content, executable=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    if executable:
        try:
            os.chmod(path, 0o755)
        except Exception:
            pass
    print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def main():
    print("=" * 60)
    print("  PHASE 12.3 — DOCKER")
    print("=" * 60)

    # Vérifier structure
    if not os.path.exists(BACKEND_DIR):
        print(f"\n  ❌ Backend introuvable : {BACKEND_DIR}")
        print("  → Le script doit être lancé depuis E:\\NAWA ECOMMERCE\\NAWA\\")
        sys.exit(1)

    if not os.path.exists(FRONTEND_DIR):
        print(f"\n  ❌ Frontend introuvable : {FRONTEND_DIR}")
        sys.exit(1)

    print("\n[1/3] Fichiers backend...")
    write_file(os.path.join(BACKEND_DIR, "Dockerfile"), BACKEND_DOCKERFILE)
    write_file(os.path.join(BACKEND_DIR, "docker-entrypoint.sh"), BACKEND_ENTRYPOINT, executable=True)
    write_file(os.path.join(BACKEND_DIR, ".dockerignore"), BACKEND_DOCKERIGNORE)
    write_file(os.path.join(BACKEND_DIR, ".env.docker"), ENV_DOCKER)

    print("\n[2/3] Fichiers frontend...")
    write_file(os.path.join(FRONTEND_DIR, "Dockerfile"), FRONTEND_DOCKERFILE)
    write_file(os.path.join(FRONTEND_DIR, "nginx-frontend.conf"), NGINX_FRONTEND)
    write_file(os.path.join(FRONTEND_DIR, ".dockerignore"), FRONTEND_DOCKERIGNORE)

    print("\n[3/3] Fichiers racine...")
    write_file(os.path.join(BASE_DIR, "docker-compose.yml"), DOCKER_COMPOSE)
    write_file(os.path.join(BASE_DIR, "deploy.ps1"), DEPLOY_SCRIPT)

    print()
    print("=" * 60)
    print("  ✅ PHASE 12.3 TERMINÉE")
    print("=" * 60)
    print("\nStructure créée :")
    print("  NAWA/")
    print("  ├── docker-compose.yml")
    print("  ├── deploy.ps1")
    print("  ├── nawa-commerce/")
    print("  │   ├── Dockerfile")
    print("  │   ├── docker-entrypoint.sh")
    print("  │   ├── .dockerignore")
    print("  │   └── .env.docker      ← À REMPLIR (SECRET_KEY)")
    print("  └── nawa-shop-frontend/")
    print("      ├── Dockerfile")
    print("      ├── nginx-frontend.conf")
    print("      └── .dockerignore")
    print()
    print("⚠️  AVANT DE LANCER :")
    print("  1. Éditer nawa-commerce/.env.docker")
    print("     → Remplacer SECRET_KEY par la vôtre")
    print("  2. Installer Docker Desktop")
    print()
    print("Puis lancer :")
    print("  cd 'E:\\NAWA ECOMMERCE\\NAWA'")
    print("  .\\deploy.ps1")


if __name__ == "__main__":
    main()