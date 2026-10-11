# Multi-Agent Production Todo Application Workflow

This document outlines the collaborative multi-agent software engineering workflow for building a full-stack, production-grade **Todo Application** across **4 autonomous Antigravity (`agy`) agents** running in parallel.

---

## 1. System Architecture & Tech Stack

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
                /api/* Requests         │                  │ /* Static Files
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

- **Backend**: Python 3.12+ / FastAPI / SQLModel / Pydantic v2 / Uvicorn / Pytest.
- **Frontend**: Modern SPA (Vite + TypeScript + React or Modern Vanilla UI) with Glassmorphism, Dark/Light mode, WCAG accessibility, and responsive typography.
- **DevOps**: Docker multi-stage builds, Docker Compose, Nginx reverse proxy, GitHub Actions CI/CD workflows, automated health check probes.
- **Advanced Features**: Subtasks, Priority Matrix, Tagging & Categories, Analytics/Productivity Dashboard, JSON/CSV Export & Import, Full-text Search.

---

## 2. Agent Allocation & Domain Isolation

To enable parallel execution across all 4 terminal instances without merge conflicts or file locking, the repository is split into strictly isolated domains:

| Agent | Terminal | Domain / Role | Isolated Directory Scope | Git Branch |
| :--- | :--- | :--- | :--- | :--- |
| **Agent 1** *(This Agent)* | Terminal PID `19204` | **Core Architecture & Backend API** | `backend/`, `contracts/`, `pyproject.toml` | `feature/backend-api` |
| **Agent 2** | Terminal 2 | **Frontend UI & Interactive Client** | `frontend/` | `feature/frontend-ui` |
| **Agent 3** | Terminal 3 | **Advanced Features & Analytics** | `features/`, `backend/app/modules/`, `frontend/src/features/` | `feature/advanced-features` |
| **Agent 4** | Terminal 4 | **DevOps, CI/CD & Production Infra** | `devops/`, `.github/`, `nginx/`, `docker-compose.yml`, `Dockerfile.*` | `feature/devops-pipeline` |

---

## 3. Directory Boundary Rules (Anti-Collision Matrix)

1. **Rule of Single Responsibility**: Each agent writes **only** to its designated directories.
2. **Contract-First Development**: Agent 1 establishes `contracts/todo-api-spec.json` and base Pydantic models. Agents 2, 3, and 4 develop against this contract.
3. **No Lock Contention**: Shared files like root `README.md` or lockfiles are updated only during the integration phase.

```
todo/
├── backend/                  <-- [AGENT 1 ONLY]
│   ├── app/
│   │   ├── core/             (Config, database session, middleware)
│   │   ├── models/           (SQLModel / SQLAlchemy entities)
│   │   ├── schemas/          (Pydantic request/response schemas)
│   │   ├── api/v1/           (CRUD endpoints: /todos, /categories, /health)
│   │   └── main.py           (FastAPI app initialization)
│   ├── tests/                (pytest suite)
│   └── requirements.txt
├── contracts/                <-- [AGENT 1 establishes, shared read-only]
│   └── todo-api-spec.json    (OpenAPI / Swagger contract)
├── frontend/                 <-- [AGENT 2 ONLY]
│   ├── src/
│   │   ├── components/       (TodoItem, TodoList, TaskModal, Header, FilterBar)
│   │   ├── services/         (ApiClient implementing contracts)
│   │   ├── styles/           (Design system, glassmorphism CSS, animations)
│   │   ├── types/            (TypeScript interfaces matching contracts)
│   │   └── App.tsx / main.ts
│   ├── public/
│   ├── index.html
│   └── package.json
├── features/                 <-- [AGENT 3 ONLY]
│   ├── subtasks/             (Checklists & subtask tracking engine)
│   ├── analytics/            (Productivity score, streaks, completion metrics)
│   ├── export_import/        (JSON / CSV data backup & restore)
│   └── search_filter/        (Advanced multi-criteria filtering & search)
├── devops/                   <-- [AGENT 4 ONLY]
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   └── nginx.conf
│   └── scripts/              (deploy.sh, backup.sh, healthcheck.sh)
├── .github/workflows/        <-- [AGENT 4 ONLY]
│   └── ci-cd.yml             (Lint, test, build, docker-smoke-test)
├── docker-compose.yml        <-- [AGENT 4 ONLY]
├── workflow.md               <-- Orchestration manual
└── README.md
```

---

## 4. Phase Execution & Synchronization Roadmap

```
  ┌──────────────────────────────────────────────────────────────┐
  │ PHASE 1: Baseline & Contracts (Agent 1)                      │
  │ - Git initialization & root commit                           │
  │ - Core FastAPI scaffolding & database schema                 │
  │ - Publish contracts/todo-api-spec.json                       │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ PHASE 2: Parallel Autonomous Sprints (All Agents)             │
  │                                                              │
  │ ┌───────────────┐ ┌───────────────┐ ┌──────────────────────┐ │
  │ │    AGENT 2    │ │    AGENT 3    │ │       AGENT 4        │ │
  │ │  Frontend UI  │ │ Adv. Features │ │ DevOps / CI/CD Infra │ │
  │ └───────┬───────┘ └───────┬───────┘ └──────────┬───────────┘ │
  └─────────┼─────────────────┼────────────────────┼─────────────┘
            │                 │                    │
            ▼                 ▼                    ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ PHASE 3: Integration & Contract Interlinking                 │
  │ - Agent 1 coordinates feature branch merges                  │
  │ - 4-Gate Quality Verification (Lint, Typecheck, Build, Test) │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │ PHASE 4: Production Release & Smoke Testing                  │
  │ - `docker compose up -d` live smoke test                     │
  │ - End-to-end API & UI functional verification                │
  └──────────────────────────────────────────────────────────────┘
```

---

## 5. Agent-by-Agent Implementation Guides & Prompts

### 🔵 Agent 1: Core Architecture & Backend API (Task 1)
* **Terminal**: Process ID `19204` (Current terminal)
* **Scope**: `backend/`, `contracts/`
* **Objective**: Build a production-grade FastAPI REST service with persistent SQLite/SQLModel storage, comprehensive validation, CRUD endpoints, filtering, pagination, and automated tests.

#### Key Deliverables:
1. `backend/app/models/todo.py`: Rich models (`Todo`, `PriorityEnum`, `StatusEnum`, `Category`).
2. `backend/app/schemas/todo.py`: Strict Pydantic v2 schemas for creation, updates, and responses.
3. `backend/app/api/v1/`: Full REST endpoints:
   - `GET /api/v1/todos` (with query filtering: status, priority, search, limit, offset)
   - `POST /api/v1/todos` (creation with validation)
   - `GET /api/v1/todos/{id}`
   - `PUT /api/v1/todos/{id}`
   - `DELETE /api/v1/todos/{id}`
   - `PATCH /api/v1/todos/{id}/toggle` (quick completion toggle)
   - `GET /api/v1/health` (live & ready probes)
4. `contracts/todo-api-spec.json`: Exported OpenAPI schema for Agent 2 and Agent 3.
5. `backend/tests/`: Pytest suite with 100% route coverage.

---

### 🟢 Agent 2: Frontend Client & UI/UX (Task 2)
* **Terminal**: Terminal 2
* **Scope**: `frontend/`
* **Prompt to copy & paste into Agent 2's terminal**:

```markdown
You are Agent 2 (Frontend Specialist) for our production Todo Application.
Your responsibility is strictly bounded to the `frontend/` directory.

### Requirements:
1. Initialize a modern, high-performance web app in `frontend/` (Vite + React + TypeScript or Modern Vanilla TS/HTML5/CSS3).
2. Adhere to our strict design aesthetic:
   - Modern glassmorphism / dark & light mode theme toggle.
   - Elegant typography (Google Fonts Inter/Outfit), smooth micro-animations, and fluid transitions.
   - Clean spacing, intuitive hover states, and accessible contrast (WCAG 2.2 AA).
3. Implement core UI components:
   - `Header`: App title, live date/time, stats badge, theme toggle.
   - `TaskInput`: Rapid task entry with priority selector (Urgent, High, Medium, Low), due date picker, category tag input, keyboard shortcut (`Enter`).
   - `FilterBar`: Filters for All / Active / Completed, sort by due date / priority / title, and search query.
   - `TodoList`: Virtualized or smooth list with empty-state illustrations.
   - `TodoItem`: Checkbox toggle, priority badge, due date display, inline edit modal, delete button with confirmation.
4. Implement `frontend/src/services/api.ts`:
   - Consumes backend endpoints at `http://localhost:8000/api/v1/todos`.
   - Includes graceful offline fallback (localStorage sync when backend is unavailable).
5. Build and verify:
   - Ensure `npm run build` passes with zero type errors.
   - Run tests or linting with 0 warnings.
```

---

### 🟡 Agent 3: Advanced Features & Analytics Engine (Task 3)
* **Terminal**: Terminal 3
* **Scope**: `features/`, `backend/app/modules/`, `frontend/src/features/`
* **Prompt to copy & paste into Agent 3's terminal**:

```markdown
You are Agent 3 (Features & Analytics Specialist) for our production Todo Application.
Your responsibility is to implement high-value advanced features that elevate the app beyond a standard todo list.

### Requirements:
1. **Subtasks & Checklist Engine**:
   - Allow any task to have multiple nested sub-tasks or checklist items.
   - Compute parent task completion percentage dynamically.
2. **Productivity & Analytics Dashboard**:
   - Daily/weekly task completion rate.
   - Productivity streak counter (consecutive active days).
   - Tasks completed vs created charts or visual breakdown.
3. **Data Import / Export**:
   - JSON export: Full backup of all tasks, categories, and settings.
   - CSV export: Export filtered lists for spreadsheets.
   - JSON import: Restore tasks with conflict resolution (overwrite or append).
4. **Tagging, Priority & Reminder Alerts**:
   - Color-coded category tags (Work, Personal, Urgent, Ideas).
   - Visual indicators for overdue tasks (amber/red glow or badges).
5. Provide modular services in `features/` with comprehensive unit tests and clean adapters for the backend and frontend.
```

---

### 🟣 Agent 4: DevOps, Infrastructure & Production Readiness (Task 4)
* **Terminal**: Terminal 4
* **Scope**: `devops/`, `.github/`, `docker-compose.yml`, `nginx/`, `.env.example`
* **Prompt to copy & paste into Agent 4's terminal**:

```markdown
You are Agent 4 (DevOps & Production Infrastructure Specialist) for our production Todo Application.
Your responsibility is to containerize, orchestrate, and automate testing and deployment for production.

### Requirements:
1. **Multi-Stage Dockerfiles**:
   - `devops/docker/backend.Dockerfile`: Lightweight Python slim image, non-root user, multi-stage build, health check probe.
   - `devops/docker/frontend.Dockerfile`: Multi-stage build with Node build step and Nginx / static file server.
2. **Production Orchestration (`docker-compose.yml`)**:
   - Services: `backend` (FastAPI), `frontend`, and `nginx-proxy` (reverse proxy routing `/api` to backend and `/` to frontend).
   - Volume mounts for persistent SQLite database (`todo_data:/app/data`).
   - Resource limits, restart policies, and healthcheck dependencies (`depends_on: condition: service_healthy`).
3. **Nginx Configuration**:
   - Reverse proxy with gzip compression, security headers (CSP, X-Frame-Options, HSTS), and client caching for static assets.
4. **CI/CD Automation (`.github/workflows/ci.yml`)**:
   - 4-Gate Quality Verification: Lint, Typecheck, Unit Tests (backend + frontend), and Docker build verification.
5. **Operational Utilities**:
   - `.env.example` with documented environment configurations.
   - Healthcheck scripts and startup verification commands.
```

---

## 6. Git Setup Guide for Parallel Terminal Execution

To ensure all 4 terminals operate in isolated working directories without clobbering each other's files, use Git Worktrees:

### Step 1: Base Commit Initialization (Done by Agent 1)
```powershell
git add .gitignore README.md workflow.md pyproject.toml
git commit -m "chore: initialize project baseline and multi-agent workflow"
```

### Step 2: Setting Up Isolated Worktrees for Agents 2, 3, and 4
Run these commands in PowerShell to create dedicated worktree folders for each agent:

```powershell
# Create worktrees directory (already gitignored)
New-Item -ItemType Directory -Force -Path .worktrees

# Agent 2 Worktree (Frontend)
git worktree add .worktrees/frontend -b feature/frontend-ui

# Agent 3 Worktree (Features)
git worktree add .worktrees/features -b feature/advanced-features

# Agent 4 Worktree (DevOps)
git worktree add .worktrees/devops -b feature/devops-pipeline
```

### Step 3: Navigating Each Terminal
- **Terminal 1 (Agent 1)**: Stay in `e:\Open-Source\TODO` (`feature/backend-api`)
- **Terminal 2 (Agent 2)**: `cd .worktrees/frontend`
- **Terminal 3 (Agent 3)**: `cd .worktrees/features`
- **Terminal 4 (Agent 4)**: `cd .worktrees/devops`

---

## 7. Self-Healing Quality Verification Gates

Before final merge to `main`, all 4 quality gates must pass with **0 errors**:

| Gate | Check | Command | Passing Criteria |
| :--- | :--- | :--- | :--- |
| **Gate 1** | Backend Lint & Tests | `pytest backend/tests -v` | All tests pass, 0 failures |
| **Gate 2** | Frontend Build & Typecheck | `npm --prefix frontend run build` | Exit code 0, no type errors |
| **Gate 3** | Docker Compose Build | `docker compose build` | Images build without errors |
| **Gate 4** | End-to-End Smoke Test | `curl http://localhost:8000/api/v1/health` | Returns `{"status": "healthy"}` |

---

## 8. Quick Status Checklist

- [ ] **Agent 1**: Baseline initialized, contracts published, FastAPI backend complete.
- [ ] **Agent 2**: Frontend UI built, glassmorphism theme verified, API integrated.
- [ ] **Agent 3**: Subtasks, Analytics Dashboard, and Import/Export functional.
- [ ] **Agent 4**: Dockerfiles, Docker Compose, Nginx, and GitHub Actions CI passing.
- [ ] **Integration**: Worktrees merged cleanly into `main`, full stack verified.
