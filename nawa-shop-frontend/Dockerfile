# ============================================================
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
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q -O /dev/null http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
