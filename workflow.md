# Multi-Agent Production Todo Application Workflow

This document defines the autonomous multi-agent engineering workflow for developing a production-grade **Full-Stack Todo Application** across parallel **Antigravity (`agy`) agents**.

---

## 1. System Architecture Overview

```
                                 ┌────────────────────────────────────────┐
                                 │            Client / Browser            │
                                 │       (Desktop & Mobile Friendly)      │
                                 └───────────────────┬────────────────────┘
                                                     │
                                                     ▼
                                 ┌────────────────────────────────────────┐
                                 │          Nginx Reverse Proxy           │
                                 │          Port 80 / 443 (Prod)          │
                                 └─────────┬──────────────────┬───────────┘
                                           │                  │
                   /api/* Requests         │                  │ /* Static Assets
                                           ▼                  ▼
                       ┌────────────────────────┐   ┌────────────────────────┐
                       │     FastAPI Backend    │   │  Modern Frontend App   │
                       │      Port 8000         │   │       Port 3000        │
                       │  (REST API + OpenAPI)  │   │   (Vite / React / UI)  │
                       └───────────┬────────────┘   └────────────────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │    SQLite / SQLModel   │
                       │  (Persistent Storage)  │
                       └────────────────────────┘
```

---

## 2. Agent Allocation & Domain Isolation

Agents 1 to 3 are dedicated to **Feature Engineering & Backend Capabilities**, while the remaining agents handle **Frontend UI** and **DevOps / Production Infrastructure**:

| Agent | Terminal | Domain / Responsibility | Isolated Path Boundary | Git Branch / Worktree |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1** *(This Agent)* | Terminal PID `19204` | **Feature Track 1: Core Architecture & Backend CRUD** | `backend/app/core/`, `backend/app/models/`, `backend/app/api/v1/todos.py`, `contracts/` | `feature/core-backend` |
| **Agent 2** | Terminal 2 | **Feature Track 2: Subtasks, Checklists & Due Dates** | `backend/app/modules/subtasks/`, `backend/app/api/v1/subtasks.py` | `feature/subtasks-reminders` |
| **Agent 3** | Terminal 3 | **Feature Track 3: Analytics, Search & Data Import/Export** | `backend/app/modules/analytics/`, `backend/app/modules/export_import/` | `feature/analytics-export` |
| **Agent 4** | Terminal 4 | **Frontend Client: Modern Responsive UI & State** | `frontend/` | `feature/frontend-ui` |
| **Agent 5** | Terminal 5 | **DevOps & Production Infra: Docker, CI/CD, Nginx** | `devops/`, `.github/`, `nginx/`, `docker-compose.yml` | `feature/devops-pipeline` |

*(Note: If running 4 agents instead of 5, Agent 4 can handle both Frontend and DevOps, or follow the 5-agent breakdown as terminal instances are available.)*

---

## 3. Directory Boundary Rules (Anti-Collision Protocol)

To eliminate git merge conflicts and file locking between parallel agents:

1. **Path Boundary Strictness**: No agent may edit code outside its designated path boundary without coordinating through interface contracts.
2. **Contract-First Development**: Agent 1 produces `contracts/todo-api-spec.json` and base Pydantic models. All downstream agents build strictly against these contracts.
3. **Dedicated Git Worktrees**: Each agent executes in its own Git worktree directory (`.worktrees/<agent-name>`), keeping the working tree clean and isolated.

```
todo/
├── contracts/                        <-- [AGENT 1: Base OpenAPI specification]
│   └── todo-api-spec.json
├── backend/
│   ├── app/
│   │   ├── core/                     <-- [AGENT 1: DB connection, settings, middleware]
│   │   ├── models/                   <-- [AGENT 1: Base Todo, Category models]
│   │   ├── schemas/                  <-- [AGENT 1: Base Pydantic schemas]
│   │   ├── api/v1/
│   │   │   ├── todos.py              <-- [AGENT 1: Base CRUD routes]
│   │   │   ├── subtasks.py           <-- [AGENT 2: Subtasks & checklist routes]
│   │   │   ├── search.py             <-- [AGENT 3: Advanced search & filters]
│   │   │   ├── analytics.py          <-- [AGENT 3: Analytics & productivity stats]
│   │   │   └── export_import.py      <-- [AGENT 3: JSON/CSV export & backup]
│   │   ├── modules/
│   │   │   ├── subtasks/             <-- [AGENT 2: Subtask domain service]
│   │   │   ├── analytics/            <-- [AGENT 3: Analytics calculation service]
│   │   │   └── export_import/        <-- [AGENT 3: Backup/export processors]
│   │   └── main.py                   <-- [AGENT 1: Application initialization]
│   └── tests/                        <-- (Respective agent tests)
├── frontend/                         <-- [AGENT 4: Entire frontend application]
│   ├── src/
│   │   ├── components/               (TodoCard, SubtaskList, StatsView, FilterBar)
│   │   ├── services/                 (API client connecting to backend)
│   │   ├── styles/                   (Glassmorphism CSS, animations, theme tokens)
│   │   └── App.tsx
│   ├── package.json
│   └── index.html
├── devops/                           <-- [AGENT 5: Container & Deployment Assets]
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── nginx.conf
│   └── scripts/                      (deploy.sh, healthcheck.sh)
├── .github/workflows/                <-- [AGENT 5: CI/CD automation]
│   └── ci.yml
└── docker-compose.yml                <-- [AGENT 5: Multi-container orchestration]
```

---

## 4. Worktree Setup for Parallel Terminals

Run these PowerShell commands in the repository root to create isolated worktrees for each agent:

```powershell
# Create worktrees directory (already gitignored)
New-Item -ItemType Directory -Force -Path .worktrees

# Agent 2 Worktree (Subtasks & Checklists feature)
git worktree add .worktrees/agent-2-subtasks -b feature/subtasks-reminders

# Agent 3 Worktree (Analytics & Export feature)
git worktree add .worktrees/agent-3-analytics -b feature/analytics-export

# Agent 4 Worktree (Frontend UI)
git worktree add .worktrees/agent-4-frontend -b feature/frontend-ui

# Agent 5 Worktree (DevOps & Production)
git worktree add .worktrees/agent-5-devops -b feature/devops-pipeline
```

Navigate each agent's terminal to its respective directory:
- **Agent 1 (Current Terminal)**: Stay in `e:\Open-Source\TODO` (`main` / `feature/core-backend`)
- **Agent 2 (Terminal 2)**: `cd .worktrees/agent-2-subtasks`
- **Agent 3 (Terminal 3)**: `cd .worktrees/agent-3-analytics`
- **Agent 4 (Terminal 4)**: `cd .worktrees/agent-4-frontend`
- **Agent 5 (Terminal 5)**: `cd .worktrees/agent-5-devops`

---

## 5. Agent Tasks & Copy-Paste Terminal Prompts

---

### 🔵 Agent 1: Feature Track 1 - Core Architecture & Backend CRUD (Task 1)
* **Terminal**: Process ID `19204` (This Agent)
* **Scope**: `backend/app/core/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/api/v1/todos.py`, `contracts/`
* **Deliverables**:
  1. FastAPI project structure with SQLModel SQLite database engine.
  2. Data models: `Todo`, `Priority` (`LOW`, `MEDIUM`, `HIGH`, `URGENT`), `Status` (`PENDING`, `IN_PROGRESS`, `COMPLETED`), `Category`.
  3. REST CRUD endpoints at `/api/v1/todos`:
     - `GET /api/v1/todos` (pagination, filter by status, category, priority)
     - `POST /api/v1/todos`
     - `GET /api/v1/todos/{id}`
     - `PUT /api/v1/todos/{id}`
     - `DELETE /api/v1/todos/{id}`
     - `PATCH /api/v1/todos/{id}/toggle`
     - `GET /api/v1/health`
  4. Generate and save `contracts/todo-api-spec.json` (OpenAPI schema).
  5. Pytest suite in `backend/tests/test_todos.py`.

---

### 🟢 Agent 2: Feature Track 2 - Subtasks, Checklists & Due Dates (Task 2)
* **Terminal**: Terminal 2 (Working in `.worktrees/agent-2-subtasks`)
* **Scope**: `backend/app/modules/subtasks/`, `backend/app/api/v1/subtasks.py`, `backend/tests/test_subtasks.py`
* **Copy-Paste Prompt for Terminal 2**:

```markdown
You are Agent 2 (Feature Specialist: Subtasks, Checklists & Due Dates) for the full-stack Todo application.
Your work is strictly isolated to your worktree (`.worktrees/agent-2-subtasks`) on branch `feature/subtasks-reminders`.

### Objective:
Implement a robust Subtask and Checklist feature for the Todo application.

### Requirements:
1. **Data Model & Schema**:
   - Model `Subtask`: `id`, `todo_id` (foreign key to Todo), `title`, `is_completed`, `order_index`, `created_at`, `updated_at`.
   - Dynamic completion calculation: When fetching a Todo, include `subtasks_count` and `subtasks_completed_count`, plus dynamic progress percentage (0-100%).
2. **API Endpoints (`backend/app/api/v1/subtasks.py`)**:
   - `GET /api/v1/todos/{todo_id}/subtasks` - List all subtasks for a todo, ordered by `order_index`.
   - `POST /api/v1/todos/{todo_id}/subtasks` - Add a new subtask to a todo.
   - `PATCH /api/v1/subtasks/{subtask_id}/toggle` - Toggle subtask completion status.
   - `PUT /api/v1/subtasks/{subtask_id}` - Edit subtask title or order.
   - `DELETE /api/v1/subtasks/{subtask_id}` - Delete a subtask.
3. **Due Dates & Reminder Metadata**:
   - Add helper logic for overdue calculations: check `due_date < current_timestamp` and `status != COMPLETED`.
   - Provide an endpoint `GET /api/v1/todos/overdue` to quickly retrieve urgent/overdue tasks.
4. **Automated Testing**:
   - Create comprehensive tests in `backend/tests/test_subtasks.py` verifying subtask creation, toggle, cascading delete, and progress percentage computation.
5. Commit your changes with descriptive commit messages and verify all tests pass.
```

---

### 🟡 Agent 3: Feature Track 3 - Analytics, Search & Data Import/Export (Task 3)
* **Terminal**: Terminal 3 (Working in `.worktrees/agent-3-analytics`)
* **Scope**: `backend/app/modules/analytics/`, `backend/app/modules/export_import/`, `backend/app/api/v1/analytics.py`, `backend/app/api/v1/export_import.py`, `backend/tests/test_features.py`
* **Copy-Paste Prompt for Terminal 3**:

```markdown
You are Agent 3 (Feature Specialist: Analytics, Search & Data Management) for the full-stack Todo application.
Your work is strictly isolated to your worktree (`.worktrees/agent-3-analytics`) on branch `feature/analytics-export`.

### Objective:
Implement high-value productivity metrics, advanced search/filtering, and full JSON/CSV data backup and restore.

### Requirements:
1. **Productivity & Analytics Engine (`backend/app/modules/analytics/`)**:
   - Endpoint `GET /api/v1/analytics/summary`:
     - Total tasks count, completed count, active count, overdue count.
     - Completion rate percentage.
     - Breakdown by priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`).
     - Breakdown by category/tag.
     - Productivity streak (consecutive days with at least 1 completed task).
2. **Advanced Search & Multi-Filter (`backend/app/api/v1/search.py`)**:
   - Endpoint `GET /api/v1/todos/search`:
     - Full-text search across title, description, and tags.
     - Multi-faceted filtering: date ranges, priority list, completion state.
     - Configurable sorting: `due_date_asc`, `priority_desc`, `created_at_desc`.
3. **Data Backup & Restore (`backend/app/modules/export_import/`)**:
   - `GET /api/v1/export/json`: Exports all todos, subtasks, and categories as a clean JSON backup.
   - `GET /api/v1/export/csv`: Exports todos as a formatted CSV spreadsheet file.
   - `POST /api/v1/import/json`: Restores or imports tasks from a JSON backup payload with conflict handling (append vs skip duplicates).
4. **Automated Testing**:
   - Create tests in `backend/tests/test_features.py` validating analytics calculations, search precision, and export/import round-trips.
5. Commit your changes with descriptive commit messages and ensure tests pass cleanly.
```

---

### 🎨 Agent 4: Frontend Application & UI/UX (Task 4)
* **Terminal**: Terminal 4 (Working in `.worktrees/agent-4-frontend`)
* **Scope**: `frontend/`
* **Copy-Paste Prompt for Terminal 4**:

```markdown
You are Agent 4 (Frontend Specialist & UI/UX Engineer) for the full-stack Todo application.
Your work is strictly isolated to your worktree (`.worktrees/agent-4-frontend`) on branch `feature/frontend-ui`.

### Objective:
Build a modern, responsive, and visually stunning web client with glassmorphism aesthetics, dark/light theme, micro-animations, and full API integration.

### Tech Stack & Guidelines:
- Modern Single-Page Application (HTML5 / TypeScript / Vite or React + Vite).
- CSS: Vanilla CSS with custom properties or CSS Modules. Rich visual hierarchy: glassmorphism cards, vibrant accents, smooth hover states, responsive mobile-to-desktop layout.
- Icons & Typography: Google Fonts (Inter or Outfit), clean SVG icons.

### Core Components & Features:
1. **App Header**:
   - App title with glowing gradient logo.
   - Live date display.
   - Quick stats pill (e.g. "4 / 7 Completed · 57%").
   - Dark/Light mode theme switch with instant transition.
2. **Quick Task Creator**:
   - Input field with instant keyboard submission (`Enter`).
   - Priority dropdown selector (Urgent: Red, High: Orange, Medium: Blue, Low: Gray).
   - Category tag badge input.
   - Due date calendar picker.
3. **Filter & Control Toolbar**:
   - Tabs: All, Active, Completed, Overdue.
   - Search bar with instant real-time filtering.
   - Sort dropdown (Due Date, Priority, Title).
   - "Analytics" toggle view button.
4. **Interactive Todo List & Items**:
   - Todo card with custom checkmark toggle and striking strike-through animation.
   - Priority indicator badges and category chips.
   - Due date status (with red warning badge for overdue tasks).
   - Expandable Subtask checklist showing progress bar (e.g. "2/3 Subtasks").
   - Action buttons: Edit modal, Delete with smooth exit transition.
5. **Analytics & Productivity View**:
   - Modal or view showing completion percentage circle, priority distribution bars, and daily streak counter.
   - Export buttons (Download JSON Backup, Download CSV).
6. **API Integration & Resilience**:
   - API client communicating with backend at `/api/v1/` (proxyable to `http://localhost:8000`).
   - Resilient offline fallback: If backend is offline, store and sync with `localStorage` gracefully.
7. Verify that `npm run build` succeeds with zero errors and clean output.
```

---

### ⚙️ Agent 5: DevOps, Infrastructure & Production Readiness (Task 5)
* **Terminal**: Terminal 5 (Working in `.worktrees/agent-5-devops`)
* **Scope**: `devops/`, `.github/`, `docker-compose.yml`, `nginx/`, `.env.example`
* **Copy-Paste Prompt for Terminal 5**:

```markdown
You are Agent 5 (DevOps & Infrastructure Specialist) for the full-stack Todo application.
Your work is strictly isolated to your worktree (`.worktrees/agent-5-devops`) on branch `feature/devops-pipeline`.

### Objective:
Package, containerize, and automate production deployment and continuous integration for the full-stack Todo application.

### Requirements:
1. **Production Multi-Stage Dockerfiles**:
   - `devops/docker/backend.Dockerfile`:
     - Python 3.12/3.13 slim base image.
     - Non-root application user for container security.
     - Production ASGI server (Uvicorn with production flags).
     - Health check directive using `curl` or python probe.
   - `devops/docker/frontend.Dockerfile`:
     - Multi-stage build: Stage 1 Node builder (`npm run build`), Stage 2 Nginx alpine server serving optimized static bundle.
2. **Docker Compose Orchestration (`docker-compose.yml`)**:
   - Services:
     - `backend`: FastAPI server exposing port 8000.
     - `frontend`: Frontend UI server exposing port 3000.
     - `proxy`: Nginx reverse proxy routing port 80/443 (`/api` -> backend, `/` -> frontend).
   - Named volume for SQLite persistence: `todo_storage:/app/data`.
   - Health check dependency: `frontend` and `proxy` wait until `backend` reports healthy.
3. **Nginx Reverse Proxy Configuration (`devops/docker/nginx.conf`)**:
   - Reverse proxy routing for API and static UI.
   - Gzip compression enabled for HTML, CSS, JS, and JSON.
   - Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`.
4. **CI/CD Pipeline (`.github/workflows/ci.yml`)**:
   - Trigger on push and pull requests to `main`.
   - Jobs:
     - Backend linting and pytest execution.
     - Frontend typecheck and build validation.
     - Docker compose build verification.
5. **Operational Utilities**:
   - `.env.example`: Documented configuration keys.
   - `devops/scripts/healthcheck.ps1` and `healthcheck.sh`: Smoke test script querying health probes.
6. Commit all changes with descriptive commit messages and test `docker-compose.yml` config validity.
```

---

## 6. Verification & Self-Healing Integration Protocol

Once all agents complete their feature sprints, the integration phase is executed:

### Quality Verification Gates:
1. **Gate 1 (Backend Tests)**:
   ```bash
   pytest backend/tests -v
   ```
   *Must exit with 0 errors and all unit/module tests passing.*

2. **Gate 2 (Frontend Build)**:
   ```bash
   npm --prefix frontend run build
   ```
   *Must compile production bundle without TypeScript errors.*

3. **Gate 3 (Docker Compose Validation)**:
   ```bash
   docker compose config
   docker compose build
   ```
   *Must parse configurations and assemble images successfully.*

4. **Gate 4 (End-to-End Smoke Test)**:
   ```bash
   docker compose up -d
   curl http://localhost/api/v1/health
   ```
   *Must return HTTP 200 with status "healthy".*

---

## 7. Execution Status Checklist

- [x] **Project Baseline**: Git initialized, root commit recorded, branches prepared.
- [ ] **Agent 1 (Current)**: Core FastAPI REST API, SQLModel schema, CRUD endpoints, OpenAPI contract.
- [ ] **Agent 2**: Subtasks, checklist progress calculation, due date logic, and tests.
- [ ] **Agent 3**: Productivity analytics, search engine, JSON/CSV export and import.
- [ ] **Agent 4**: Responsive frontend application, glassmorphism theme, API client integration.
- [ ] **Agent 5**: Multi-stage Dockerfiles, Docker Compose, Nginx proxy, GitHub Actions CI.
- [ ] **Integration**: All feature worktrees merged cleanly into `main`, production stack verified.
