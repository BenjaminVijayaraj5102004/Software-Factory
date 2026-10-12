# ==============================================================================
# Production Build & Deployment Script (PowerShell / Windows)
# ==============================================================================

Write-Host "==> Validating Docker Compose configuration..." -ForegroundColor Cyan
docker compose config | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker Compose validation failed."
    exit 1
}

Write-Host "==> Building production images with Docker Compose..." -ForegroundColor Cyan
docker compose build
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker Compose build failed."
    exit 1
}

Write-Host "==> Starting production stack in detached mode..." -ForegroundColor Cyan
docker compose up -d --remove-orphans

Write-Host "==> Stack status:" -ForegroundColor Cyan
docker compose ps

Write-Host "==> Stack is ready. Visit http://localhost (Gateway) or http://localhost:8000/docs (API Docs)." -ForegroundColor Green
