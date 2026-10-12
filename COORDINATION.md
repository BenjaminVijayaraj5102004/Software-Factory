# Multi-Agent Coordination & Architecture Workflow Board

**Lead / Senior Project Manager Agent**: `f8cab4fa-29a9-4f0f-af99-57dfe1bb0ade`  
**Project**: Full-Stack Todo Application (FastAPI + SQLModel SQLite + Neo-Brutalist React UI + Docker/CI/CD)  
**Status**: ACTIVE SPRINT COORDINATION

---

## 1. Active Terminal Agents & Architectural Boundaries

To avoid code overwrites and merge collisions, all agents must operate within their strict domain boundaries:

| Agent Role | Agent Conversation ID | Isolated Path Boundary | Key Responsibilities | Dependency Mandate |
| :--- | :--- | :--- | :--- | :--- |
| **Backend & Database** | `f7a02c8a-3edb-41bd-a8b7-6ebd89c05abb` | `backend/app/core/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/api/v1/` | FastAPI initialization, SQLite engine (`data/todo.db`), SQLModel tables, CORS setup, CRUD routes. | **MUST register all core backend dependencies in `requirements.txt`** |
| **Advanced Features** | `c94f5dc4-b308-4ed1-bf26-60523c888381` | `backend/app/modules/subtasks/`, `backend/app/modules/analytics/`, `backend/app/modules/export_import/` | Subtask checklist logic, filtering, search query engine, CSV/JSON export & import endpoints. | **MUST append any additional Python packages to `requirements.txt`** |
| **Frontend UI/UX** | `aded5139-578e-4939-a28e-a56dfc547efb` | `frontend/` | Neo-Brutalism + Glassmorphic responsive UI (React + TS + Vite). State management, API sync, offline fallback, build verified in `frontend/dist`. **[COMPLETED & VERIFIED]** | Manage via `frontend/package.json` |
| **DevOps & CI/CD** | `72a8572b-82a5-47c7-8cdf-a191713d374f` | `devops/`, `.github/`, `docker-compose.yml`, `nginx/` | Production Dockerfiles, docker-compose orchestration, Nginx reverse proxy, GitHub Actions CI. | Use `requirements.txt` in Dockerfile & CI |
| **Senior Project Manager** | `f8cab4fa-29a9-4f0f-af99-57dfe1bb0ade` | Root / `requirements.txt`, `workflow.md`, `COORDINATION.md` | Sprint orchestration, architectural alignment, dependency hygiene verification. | Master overseer |

---

## 2. Dependency Management Mandate (`requirements.txt`)

> [!IMPORTANT]
> **MANDATORY POLICY FOR BACKEND & FEATURES AGENTS**:
> All Python package dependencies must be explicitly added to `requirements.txt` in the root repository.
> Do NOT install packages in ad-hoc environments without updating `requirements.txt`.
> The DevOps Docker builds and CI test suites rely directly on `requirements.txt`.

### Current Baseline `requirements.txt`:
```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlmodel>=0.0.22
pydantic>=2.8.0
pydantic-settings>=2.4.0
python-multipart>=0.0.9
httpx>=0.27.0
pytest>=8.3.0
```

---

## 3. Architecture Workflow Protocol

```
                        ┌────────────────────────────────────────┐
                        │        Client: Frontend (Vite)         │
                        │      Neo-Brutalism + Glass (Port 3000) │
                        └───────────────────┬────────────────────┘
                                            │
                                            ▼
                        ┌────────────────────────────────────────┐
                        │          Nginx Reverse Proxy           │
                        │           Port 80 / Gateway            │
                        └─────────┬──────────────────┬───────────┘
                                  │                  │
                /api/v1/* Requests│                  │ /* Static UI (dist/)
                                  ▼                  ▼
              ┌─────────────────────────┐      ┌─────────────────────────┐
              │     FastAPI Backend     │      │     Built Frontend      │
              │  Port 8000 (Backend +   │      │        (Nginx)          │
              │     Features Modules)   │      └─────────────────────────┘
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    SQLite Database      │
              │     (SQLModel ORM)      │
              └─────────────────────────┘
```

---

## 4. Shared API Contracts (`/api/v1`)

All agents adhere to the following contract structure:
- Health check: `GET /api/v1/health` -> `{"status": "healthy", "database": "connected"}`
- Categories: `GET /api/v1/categories`, `POST /api/v1/categories`
- Todos: `GET /api/v1/todos`, `POST /api/v1/todos`, `GET /api/v1/todos/{id}`, `PUT /api/v1/todos/{id}`, `DELETE /api/v1/todos/{id}`
- Subtasks: `POST /api/v1/todos/{id}/subtasks`, `PATCH /api/v1/subtasks/{subtask_id}`
- Analytics: `GET /api/v1/analytics/stats`
- Export / Import: `GET /api/v1/export/json`, `GET /api/v1/export/csv`, `POST /api/v1/import/json`

---

## 5. Live Message Bus Log
- **Frontend Agent -> DevOps**: Confirmed build output `frontend/dist/` on port 3000.
- **Frontend Agent -> Backend**: Requested CORS for `http://localhost:3000` and `http://localhost:5173`.
- **PM Agent -> All Agents**: Architecture workflow review initiated. Baseline `requirements.txt` published. Strict domain boundaries enforced.
- **Backend Agent -> DevOps**: Confirmed FastAPI entrypoint `backend.app.main:app`, port 8000, SQLite volume at `/app/data/todo.db`, and healthcheck probe at `GET /api/v1/health`.
- **Features Agent -> DevOps**: Confirmed standard test runner `pytest backend/tests -v` with no extra system packages.
- **DevOps Agent -> All Agents**: Completed production Docker infrastructure:
  1. `devops/docker/backend.Dockerfile`: Python 3.12-slim, non-root user `appuser`, SQLite persistence at `/app/data`, Uvicorn ASGI server, health checks hitting `/api/v1/health`.
  2. `devops/docker/frontend.Dockerfile`: Multi-stage build (Node 20 builder -> Nginx 1.27 Alpine runner), SPA fallback routing, `/healthz` probe.
  3. `devops/docker/nginx.conf`: Production gateway on port 80 routing `/api/` and Swagger docs to Backend (8000) and `/` to Frontend (3000), gzip compression, security headers.
  4. `docker-compose.yml`: Multi-container orchestration, health checks, dependency ordering (`condition: service_healthy`), SQLite volume `todo_storage`.
  5. `.github/workflows/ci.yml`: Full CI/CD pipeline covering Backend Lint & Pytest, Frontend Build, and Docker Compose validation.
  6. Operational automation: `devops/scripts/healthcheck.ps1`, `devops/scripts/healthcheck.sh`, `devops/scripts/deploy.ps1`, `devops/scripts/deploy.sh`, and `devops/README.md`.
  7. Verification: Backend pytest suite passed (18 passed in 1.59s), `docker compose config` syntax validated with 0 errors.
- **Frontend Agent -> All Agents**: Completed responsive Neo-Brutalism & Glass UI:
  1. Design system implemented in `frontend/src/styles/theme.css`: solid 2.5px borders, unblurred 4px/6px hard drop shadows, tactile hover/active press animations, frosted glass surfaces (`backdrop-filter: blur(14px)`), and vivid glass color accents (Butter Yellow, Mint Sage, Electric Lavender, Neon Cyan, Sunset Coral).
  2. Component architecture: `Header` (live clock, completion progress bar, API connection probe, theme switch), `TaskCreator` (tactile quick-add with priority chips & calendar date picker), `FilterToolbar` (All/Active/Completed/Overdue tabs, instant search bar, category chips, sort selector), `TodoCard` (tactile checkbox, strikethrough animation, subtask checklist with mini progress bar, edit/delete actions), `EditTaskModal`, `AnalyticsModal` (completion rates, streak counter, JSON/CSV exports), and `Toast` notifications.
  3. API service layer: `frontend/src/services/api.ts` connecting to `/api/v1/todos`, `/api/v1/categories`, `/api/v1/health`, and `/api/v1/export/*` with seamless local storage offline cache and automatic sync on reconnect.
- **Backend & Database Connection Agent -> All Agents**: Completed SQLite database engine, service layer, CORS connectivity, and API verification:
  1. SQLite Database Architecture: Configured `backend/app/core/database.py` with `PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;`, and `PRAGMA synchronous = NORMAL;` for high-concurrency read/write operations without database locking. Auto-initializes directory paths and seeds default categories.
  2. Data Models & Schemas: Built SQLModel entities for `Todo`, `Category`, `Subtask` with cascading delete relationships and full Pydantic request/response validation schemas.
  3. Service Layer Architecture: Decoupled service layer in `backend/app/services/` (`todo_service.py`, `category_service.py`, `subtask_service.py`) owning business logic, pagination, enrichment, and stats calculation.
  4. Connection Endpoints & CORS: Mounted `/api/v1/health` (live DB connectivity + entity counts probe), `/api/v1/todos` (CRUD, status toggle, filtering, sorting, pagination), `/api/v1/categories`, and `/api/v1/todos/{id}/subtasks`. Configured CORS middleware for `http://localhost:3000`, `http://localhost:5173`, `http://127.0.0.1:3000`, `http://127.0.0.1:5173`, and `*`.
  5. Test Verification: Full Pytest test suite executed cleanly with **31 out of 31 tests passing** (`test_connection.py`, `test_features.py`, `test_todos.py`) verifying WAL mode, foreign keys integrity, cascading subtask deletions, CORS headers, and CRUD lifecycle.
- **DevOps Agent -> All Agents**: Audited and hardened CI workflow in `.github/workflows/ci.yml`:
  1. Resolved npm ci failure by checking `frontend/package.json` existence before install and adding fallback to `npm install`.
  2. Hardened `devops/docker/frontend.Dockerfile` with fallback handling.
  3. Added `.dockerignore` to exclude `.venv`, `node_modules`, and cache directories from build contexts.
  4. Added `PYTHONPATH: .` to pytest step.
  5. Integrated full backend and frontend code trees into `devops` branch, re-verified 31/31 pytest tests and `npm run build`, and pushed update to `origin/devops`.
  6. Fixed `docker-ci` step by removing non-existent action `actions/setup-buildx-action@v3`, relying on Ubuntu runner's native Docker & Compose engine.
---

## 6. GitHub Pull Requests & Delivery Tracking

All 4 feature branches have been pushed to remote repository `origin` (`https://github.com/BenjaminVijayaraj5102004/Software-factory.git`). Pull Requests are ready for review and merge:

| Track / Domain | Feature Branch | Target Base | Direct GitHub PR Creation Link | Verification & Test Gates |
| :--- | :--- | :--- | :--- | :--- |
| **Backend & Database** | `backend-connection` | `main` | [Create Backend PR](https://github.com/BenjaminVijayaraj5102004/Software-factory/pull/new/backend-connection) | 31/31 Pytest tests passed; SQLite WAL mode & foreign keys verified; dependencies locked in `requirements.txt`. |
| **Advanced Features** | `features-advanced` | `main` | [Create Features PR](https://github.com/BenjaminVijayaraj5102004/Software-factory/pull/new/features-advanced) | 31/31 Pytest tests passed; subtask checklist progress, analytics, and JSON/CSV export/import verified; 25 OpenAPI contracts valid. |
| **Frontend UI/UX** | `frontend` | `main` | [Create Frontend PR](https://github.com/BenjaminVijayaraj5102004/Software-factory/pull/new/frontend) | Neo-Brutalist & Glass theme; `npm run build` compiled 0 errors to `frontend/dist`; dual-mode offline sync tested. |
| **DevOps & CI/CD** | `devops` | `main` | [Create DevOps PR](https://github.com/BenjaminVijayaraj5102004/Software-factory/pull/new/devops) | Multi-stage Dockerfiles (`backend.Dockerfile`, `frontend.Dockerfile`); `docker compose config` passed 0 errors; CI workflow active. |

---
