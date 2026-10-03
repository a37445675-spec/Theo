# ============================================================
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
