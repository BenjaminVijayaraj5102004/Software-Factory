# Todo application

A full-stack task manager built with FastAPI, SQLite, and a React frontend.

## Prerequisites

Install the following tools before you begin:

- Python 3.12 or newer
- Node.js 20 or newer
- Docker and Docker Compose (optional, for container runs)

## Quick start with Docker

The fastest way to run the entire stack is with Docker Compose.

1. Clone the repository and enter the directory:

```bash
git clone https://github.com/BenjaminVijayaraj5102004/Software-factory.git
cd Software-factory
```

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Build and launch the containers:

```bash
docker compose up --build
```

4. Open your browser:

- Web application: http://localhost
- API documentation: http://localhost/docs
- Health check: http://localhost/api/v1/health

To stop the containers, press `Ctrl+C` or run:

```bash
docker compose down
```

## Manual local setup

If you prefer to develop without Docker, run the backend and frontend in separate terminal windows.

### 1. Backend setup

1. Create a Python virtual environment in the project root:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:
```bash
source .venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

The backend starts at http://localhost:8000. Interactive Swagger documentation is available at http://localhost:8000/docs.

### 2. Frontend setup

1. Open a second terminal window and move into the `frontend` directory:

```bash
cd frontend
```

2. Install the JavaScript packages:

```bash
npm install
```

3. Start the Vite development server:

```bash
npm run dev
```

The frontend starts at http://localhost:3000. It proxies requests to the backend at http://localhost:8000.

## Running tests

Run the test suites to confirm your local setup works.

### Backend tests

Activate your virtual environment and run pytest from the root folder:

```bash
pytest backend/tests -v
```

On Windows, if pytest cannot locate the `backend` module, set `PYTHONPATH` before running:

```powershell
$env:PYTHONPATH = "."
pytest backend/tests -v
```

### Frontend build verification

Confirm that the TypeScript types check and Vite compiles without errors:

```bash
cd frontend
npm run build
```

The production bundle outputs to `frontend/dist/`.

## Environment variables

Create a `.env` file in the root folder to override defaults:

| Variable | Default value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./todo.db` | SQLite database connection string. |
| `API_V1_STR` | `/api/v1` | URL prefix for version 1 API endpoints. |
| `PORT` | `80` | Port for the production Nginx reverse proxy. |
| `BACKEND_PORT` | `8000` | Port for the FastAPI server. |
| `FRONTEND_PORT` | `3000` | Port for the frontend development server. |

## Project layout

```text
├── backend/
│   ├── app/
│   │   ├── api/v1/         # Route handlers (todos, categories, health)
│   │   ├── core/           # Database setup and configuration
│   │   ├── models/         # SQLModel database tables
│   │   ├── modules/        # Feature services (subtasks, analytics, export)
│   │   ├── schemas/        # Pydantic request and response schemas
│   │   └── services/       # Business logic layer
│   └── tests/              # Backend test suite
├── frontend/
│   ├── src/
│   │   ├── components/     # React UI components
│   │   ├── services/       # API client with offline storage support
│   │   └── styles/         # CSS styles and theme variables
│   └── package.json
├── devops/
│   ├── docker/             # Dockerfiles and Nginx configuration
│   └── scripts/            # Deployment and health check scripts
├── docker-compose.yml       # Container orchestration
├── requirements.txt         # Pinned Python dependencies
└── README.md
```
