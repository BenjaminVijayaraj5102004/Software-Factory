#!/usr/bin/env bash
# ==============================================================================
# Production Build & Deployment Script (Linux / macOS / Bash)
# ==============================================================================

set -euo pipefail

echo "==> Validating Docker Compose configuration..."
docker compose config > /dev/null

echo "==> Building production images with Docker Compose..."
docker compose build --pull

echo "==> Starting production stack in detached mode..."
docker compose up -d --remove-orphans

echo "==> Waiting for backend healthcheck probe..."
RETRIES=15
until docker compose ps | grep -E "todo-backend.*healthy" > /dev/null || [ $RETRIES -eq 0 ]; do
    echo "Waiting for backend to become healthy... ($RETRIES retries left)"
    sleep 3
    RETRIES=$((RETRIES - 1))
done

echo "==> Stack status:"
docker compose ps

echo "==> Stack is ready. Visit http://localhost (Gateway) or http://localhost:8000/docs (API Docs)."
