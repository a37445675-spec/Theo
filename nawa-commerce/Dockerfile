# ============================================================
#  NAWA Commerce — Backend Dockerfile
#  Python 3.11 + Django 5 + Gunicorn
# ============================================================
FROM python:3.11-slim AS builder

# Dépendances système pour build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements d'abord (cache Docker)
COPY requirements.txt .

# Installer dans un venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn whitenoise


# ============================================================
#  IMAGE FINALE
# ============================================================
FROM python:3.11-slim

# Dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    curl \
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
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R nawa:nawa /app/staticfiles /app/media /app/logs

USER nawa

# Variables d'environnement par défaut
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings_production

# Port exposé
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/design-system/active/ || exit 1

# Script de démarrage
COPY --chown=nawa:nawa docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
