from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.app.models.enums import Priority, Status


def test_health_check(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Production Todo API" in data["app"]
    assert "/docs" in data["docs"]


def test_create_todo_minimal(client: TestClient):
    payload = {"title": "Buy groceries"}
    response = client.post("/api/v1/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Buy groceries"
    assert data["status"] == Status.PENDING
    assert data["priority"] == Priority.MEDIUM
    assert data["is_overdue"] is False
    assert data["subtasks_count"] == 0


def test_create_todo_full(client: TestClient):
    due = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    payload = {
        "title": "Complete Multi-Agent System",
        "description": "Orchestrate agents across backend, frontend, devops",
        "priority": "URGENT",
        "status": "IN_PROGRESS",
        "due_date": due,
        "tags": "dev,multi-agent",
        "category_name": "Engineering",
    }
    response = client.post("/api/v1/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete Multi-Agent System"
    assert data["priority"] == "URGENT"
    assert data["status"] == "IN_PROGRESS"
    assert data["category"] is not None
    assert data["category"]["name"] == "Engineering"
    assert data["tags"] == "dev,multi-agent"


def test_get_todo_by_id(client: TestClient):
    # Create first
    created = client.post("/api/v1/todos", json={"title": "Single Todo Test"}).json()
    todo_id = created["id"]

    # Fetch
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Single Todo Test"


def test_get_todo_not_found(client: TestClient):
    response = client.get("/api/v1/todos/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_todos_pagination_and_sorting(client: TestClient):
    # Populate test items
    client.post("/api/v1/todos", json={"title": "Task A", "priority": "LOW"})
    client.post("/api/v1/todos", json={"title": "Task B", "priority": "HIGH"})
    client.post("/api/v1/todos", json={"title": "Task C", "priority": "URGENT"})

    # Paginate with limit 2
    response = client.get("/api/v1/todos?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total_pages"] == 2

    # Second page
    response_p2 = client.get("/api/v1/todos?page=2&limit=2")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert len(data_p2["items"]) == 1


def test_filter_by_status_and_priority(client: TestClient):
    client.post("/api/v1/todos", json={"title": "Pending Item", "status": "PENDING", "priority": "LOW"})
    client.post("/api/v1/todos", json={"title": "Completed Item", "status": "COMPLETED", "priority": "URGENT", "category_name": "Work"})

    # Filter status
    res_completed = client.get("/api/v1/todos?status=COMPLETED")
    assert res_completed.status_code == 200
    assert res_completed.json()["total"] == 1
    assert res_completed.json()["items"][0]["title"] == "Completed Item"

    # Filter priority
    res_urgent = client.get("/api/v1/todos?priority=URGENT")
    assert res_urgent.status_code == 200
    assert res_urgent.json()["total"] == 1
    assert res_urgent.json()["items"][0]["title"] == "Completed Item"

    # Filter category
    res_work = client.get("/api/v1/todos?category=Work")
    assert res_work.status_code == 200
    assert res_work.json()["total"] == 1
    assert res_work.json()["items"][0]["title"] == "Completed Item"


def test_search_todos(client: TestClient):
    client.post("/api/v1/todos", json={"title": "Deploy Docker Container", "tags": "devops"})
    client.post("/api/v1/todos", json={"title": "Refactor React Components", "tags": "frontend"})

    response = client.get("/api/v1/todos?search=Docker")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Deploy Docker Container"


def test_update_todo(client: TestClient):
    created = client.post("/api/v1/todos", json={"title": "Original Title"}).json()
    todo_id = created["id"]

    update_payload = {
        "title": "Updated Title",
        "status": "COMPLETED",
        "priority": "HIGH",
    }
    response = client.put(f"/api/v1/todos/{todo_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "COMPLETED"
    assert data["priority"] == "HIGH"
    assert data["completed_at"] is not None


def test_update_todo_not_found(client: TestClient):
    response = client.put("/api/v1/todos/8888", json={"title": "Ghost"})
    assert response.status_code == 404


def test_toggle_todo(client: TestClient):
    created = client.post("/api/v1/todos", json={"title": "Toggle Item"}).json()
    todo_id = created["id"]
    assert created["status"] == "PENDING"
    assert created["completed_at"] is None

    # First toggle -> COMPLETED
    toggle_1 = client.patch(f"/api/v1/todos/{todo_id}/toggle")
    assert toggle_1.status_code == 200
    data_1 = toggle_1.json()
    assert data_1["status"] == "COMPLETED"
    assert data_1["completed_at"] is not None

    # Second toggle -> PENDING
    toggle_2 = client.patch(f"/api/v1/todos/{todo_id}/toggle")
    assert toggle_2.status_code == 200
    data_2 = toggle_2.json()
    assert data_2["status"] == "PENDING"
    assert data_2["completed_at"] is None


def test_toggle_todo_not_found(client: TestClient):
    response = client.patch("/api/v1/todos/99999/toggle")
    assert response.status_code == 404


def test_delete_todo(client: TestClient):
    created = client.post("/api/v1/todos", json={"title": "To Be Deleted"}).json()
    todo_id = created["id"]

    # Delete
    del_res = client.delete(f"/api/v1/todos/{todo_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == todo_id

    # Verify not found
    get_res = client.get(f"/api/v1/todos/{todo_id}")
    assert get_res.status_code == 404


def test_delete_todo_not_found(client: TestClient):
    response = client.delete("/api/v1/todos/99999")
    assert response.status_code == 404


def test_categories_api(client: TestClient):
    # Create category
    cat_payload = {"name": "Work", "color": "#10b981", "icon": "briefcase"}
    create_res = client.post("/api/v1/todos/categories", json=cat_payload)
    assert create_res.status_code == 201
    cat_data = create_res.json()
    assert cat_data["name"] == "Work"
    assert cat_data["color"] == "#10b981"

    # List categories
    list_res = client.get("/api/v1/todos/categories")
    assert list_res.status_code == 200
    categories = list_res.json()
    assert len(categories) >= 1
    assert any(c["name"] == "Work" for c in categories)


def test_overdue_calculation(client: TestClient):
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    # Past due & pending -> should be overdue
    overdue_item = client.post(
        "/api/v1/todos",
        json={"title": "Overdue Task", "due_date": past_date, "status": "PENDING"},
    ).json()
    assert overdue_item["is_overdue"] is True

    # Future due & pending -> should NOT be overdue
    future_item = client.post(
        "/api/v1/todos",
        json={"title": "Future Task", "due_date": future_date, "status": "PENDING"},
    ).json()
    assert future_item["is_overdue"] is False

    # Past due & completed -> should NOT be overdue
    completed_item = client.post(
        "/api/v1/todos",
        json={"title": "Completed Past Task", "due_date": past_date, "status": "COMPLETED"},
    ).json()
    assert completed_item["is_overdue"] is False


def test_direct_categories_endpoint(client: TestClient):
    cat_payload = {"name": "Personal", "color": "#3b82f6"}
    res = client.post("/api/v1/categories", json=cat_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Personal"
    assert data["color"] == "#3b82f6"

    # Fetch list
    list_res = client.get("/api/v1/categories")
    assert list_res.status_code == 200
    names = [c["name"] for c in list_res.json()]
    assert "Personal" in names

