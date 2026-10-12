# DevOps & Infrastructure Documentation

Production-grade containerization and CI/CD pipelines for the Full-Stack Todo Application.

---

## 1. Architecture Overview

```
                                 ┌────────────────────────────────────────┐
                                 │            Client / Browser            │
                                 │       (Desktop & Mobile Friendly)      │
                                 └───────────────────┬────────────────────┘
                                                     │
                                                     ▼
                                 ┌────────────────────────────────────────┐
                                 │          Nginx Reverse Proxy           │
                                 │               Port 80                  │
                                 └─────────┬──────────────────┬───────────┘
                                           │                  │
                   /api/* Requests         │                  │ /* Static UI
                                           ▼                  ▼
                       ┌────────────────────────┐   ┌────────────────────────┐
                       │     FastAPI Backend    │   │  Frontend React App    │
                       │      Port 8000         │   │  (Nginx Alpine Runner) │
                       │  (REST API + OpenAPI)  │   │       Port 3000        │
                       └───────────┬────────────┘   └────────────────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │    SQLite Persistent   │
                       │     Storage Volume     │
                       │  (/app/data/todo.db)   │
                       └────────────────────────┘
```

---

## 2. Infrastructure Components

### Multi-Stage Dockerfiles
- **`devops/docker/backend.Dockerfile`**:
  - Base: `python:3.12-slim`
  - Non-root user: `appuser` (UID 1000)
  - ASGI Server: `uvicorn backend.app.main:app`
  - Health probe: `curl -f http://localhost:8000/api/v1/health`
  - SQLite mount path: `/app/data`
- **`devops/docker/frontend.Dockerfile`**:
  - Multi-stage build (`node:20-alpine` builder, `nginx:1.27-alpine` runner)
  - Configurable `VITE_API_URL` build argument
  - Single Page Application routing fallback to `index.html`
- **`devops/docker/nginx.conf`**:
  - Reverse proxy gateway listening on port 80
  - Reverse proxy to backend upstream on `/api/`
  - Reverse proxy to Swagger/OpenAPI docs (`/docs`, `/redoc`, `/openapi.json`)
  - Reverse proxy to frontend upstream on `/`
  - Gzip compression and hardened security headers

---

## 3. Quick Start Commands

### Validate Configurations
```bash
docker compose config
```

### Build and Start Stack
```bash
# Using helper scripts
./devops/scripts/deploy.sh       # Linux / macOS
.\devops\scripts\deploy.ps1      # Windows PowerShell

# Or directly with Docker Compose
docker compose up -d --build
```

### Run Health Smoke Tests
```bash
./devops/scripts/healthcheck.sh  # Linux / macOS
.\devops\scripts\healthcheck.ps1 # Windows PowerShell
```

### Stop Stack
```bash
docker compose down
```

---

## 4. Continuous Integration Pipeline

Defined in `.github/workflows/ci.yml`:
- **Backend Job**: Sets up Python 3.12, installs dependencies, lints with Ruff, executes pytest suite.
- **Frontend Job**: Sets up Node.js 20, installs npm dependencies, typechecks and runs `npm run build`.
- **Docker Job**: Validates `docker compose config` syntax and compiles container images.
