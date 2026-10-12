import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select, text

from backend.app.core.database import engine, init_db
from backend.app.models.category import Category
from backend.app.models.enums import Priority, Status
from backend.app.models.subtask import Subtask
from backend.app.models.todo import Todo


def test_sqlite_pragmas_and_wal_mode():
    """Verify SQLite WAL mode and foreign key constraints are active."""
    # Initialize disk database
    init_db()
    with Session(engine) as session:
        wal_result = session.exec(text("PRAGMA journal_mode;")).first()
        assert wal_result is not None
        assert wal_result[0].lower() in ["wal", "memory"]

        fk_result = session.exec(text("PRAGMA foreign_keys;")).first()
        assert fk_result is not None
        assert fk_result[0] == 1


def test_database_tables_exist():
    """Verify core SQLModel tables exist in SQLite master."""
    init_db()
    with Session(engine) as session:
        tables = session.exec(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        ).all()
        table_names = [t[0] for t in tables]
        assert "todo" in table_names
        assert "category" in table_names
        assert "subtask" in table_names


def test_default_categories_seeded():
    """Verify database seeding created default categories."""
    init_db()
    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        assert len(categories) >= 4
        cat_names = [c.name for c in categories]
        assert "Work" in cat_names
        assert "Personal" in cat_names


def test_health_check_returns_database_connected(client: TestClient):
    """Verify /api/v1/health probe queries SQLite and returns healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "todos_count" in data
    assert "categories_count" in data


def test_cors_headers_allow_frontend_origins(client: TestClient):
    """Verify CORS middleware permits frontend requests from localhost:3000 and 5173."""
    response = client.options(
        "/api/v1/todos",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    allowed_origin = response.headers["access-control-allow-origin"]
    assert allowed_origin in ["http://localhost:3000", "*"]


def test_end_to_end_todo_subtask_lifecycle(client: TestClient, session: Session):
    """Full lifecycle: create category, create todo, add subtask, toggle, delete with cascade."""
    # 1. Create a category
    cat_resp = client.post(
        "/api/v1/categories",
        json={"name": "Integration Test Cat", "color": "#10B981", "icon": "tag"},
    )
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()["id"]

    # 2. Create a Todo with that category
    todo_resp = client.post(
        "/api/v1/todos",
        json={
            "title": "Connected Architecture Verification",
            "description": "Verifying frontend-backend connection to SQLite",
            "priority": "HIGH",
            "status": "PENDING",
            "category_id": cat_id,
        },
    )
    assert todo_resp.status_code == 201
    todo_data = todo_resp.json()
    todo_id = todo_data["id"]
    assert todo_data["title"] == "Connected Architecture Verification"
    assert todo_data["category_id"] == cat_id

    # 3. Add Subtask
    sub_resp = client.post(
        f"/api/v1/todos/{todo_id}/subtasks",
        json={"title": "Configure SQLite WAL pragma", "is_completed": False},
    )
    assert sub_resp.status_code == 201
    sub_id = sub_resp.json()["id"]

    # 4. Toggle Subtask
    toggle_sub = client.patch(f"/api/v1/subtasks/{sub_id}/toggle")
    assert toggle_sub.status_code == 200
    assert toggle_sub.json()["is_completed"] is True

    # 5. Toggle Todo
    toggle_todo = client.patch(f"/api/v1/todos/{todo_id}/toggle")
    assert toggle_todo.status_code == 200
    assert toggle_todo.json()["status"] == "COMPLETED"

    # 6. Verify Todo enriched stats
    get_todo = client.get(f"/api/v1/todos/{todo_id}")
    assert get_todo.status_code == 200
    enriched = get_todo.json()
    assert enriched["subtasks_count"] == 1
    assert enriched["subtasks_completed_count"] == 1
    assert enriched["progress_percentage"] == 100.0

    # 7. Delete Todo and verify cascading deletion of subtask
    del_resp = client.delete(f"/api/v1/todos/{todo_id}")
    assert del_resp.status_code == 200

    # Subtask should no longer exist in session
    remaining_subtask = session.get(Subtask, sub_id)
    assert remaining_subtask is None
