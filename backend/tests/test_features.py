from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest


def test_todo_update_full(client: TestClient):
    """Verify full update of a todo via PUT."""
    created = client.post("/api/v1/todos", json={"title": "Original Title", "priority": "LOW"}).json()
    todo_id = created["id"]

    update_payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "priority": "URGENT",
        "status": "IN_PROGRESS",
    }
    put_res = client.put(f"/api/v1/todos/{todo_id}", json=update_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["priority"] == "URGENT"
    assert data["status"] == "IN_PROGRESS"


def test_todo_patch_partial_and_is_completed(client: TestClient):
    """Verify partial PATCH update, including boolean is_completed toggling."""
    created = client.post(
        "/api/v1/todos", json={"title": "Patchable Task", "status": "PENDING"}
    ).json()
    todo_id = created["id"]
    assert created["is_completed"] is False

    # Partial title update
    patch_title = client.patch(f"/api/v1/todos/{todo_id}", json={"title": "Renamed Task"})
    assert patch_title.status_code == 200
    assert patch_title.json()["title"] == "Renamed Task"
    assert patch_title.json()["status"] == "PENDING"

    # Toggle to completed via is_completed flag
    patch_complete = client.patch(f"/api/v1/todos/{todo_id}", json={"is_completed": True})
    assert patch_complete.status_code == 200
    comp_data = patch_complete.json()
    assert comp_data["is_completed"] is True
    assert comp_data["status"] == "COMPLETED"
    assert comp_data["completed_at"] is not None

    # Toggle back to pending
    patch_pending = client.patch(f"/api/v1/todos/{todo_id}", json={"is_completed": False})
    assert patch_pending.status_code == 200
    pend_data = patch_pending.json()
    assert pend_data["is_completed"] is False
    assert pend_data["status"] == "PENDING"
    assert pend_data["completed_at"] is None


def test_todo_delete_cascades_subtasks(client: TestClient):
    """Verify deleting a todo removes the todo and its associated subtasks."""
    todo = client.post("/api/v1/todos", json={"title": "Parent Todo"}).json()
    todo_id = todo["id"]

    # Add 2 subtasks
    sub1 = client.post(f"/api/v1/todos/{todo_id}/subtasks", json={"title": "Subtask A"}).json()
    sub2 = client.post(f"/api/v1/todos/{todo_id}/subtasks", json={"title": "Subtask B"}).json()

    # Delete parent todo
    del_res = client.delete(f"/api/v1/todos/{todo_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == todo_id

    # Verify todo is deleted
    assert client.get(f"/api/v1/todos/{todo_id}").status_code == 404

    # Verify subtasks are removed and query returns empty list
    subtasks_res = client.get(f"/api/v1/todos/{todo_id}/subtasks")
    assert subtasks_res.status_code == 200
    assert subtasks_res.json() == []


def test_subtasks_crud_and_progress_calculation(client: TestClient):
    """Verify subtask lifecycle, toggling, and progress percentage computation."""
    todo = client.post("/api/v1/todos", json={"title": "Checklist Project"}).json()
    todo_id = todo["id"]

    # Create subtasks
    s1 = client.post(f"/api/v1/todos/{todo_id}/subtasks", json={"title": "Step 1", "is_completed": False}).json()
    s2 = client.post(f"/api/v1/todos/{todo_id}/subtasks", json={"title": "Step 2", "is_completed": False}).json()

    # Check initial progress on todo
    t_check = client.get(f"/api/v1/todos/{todo_id}").json()
    assert t_check["subtasks_count"] == 2
    assert t_check["subtasks_completed_count"] == 0
    assert t_check["progress_percentage"] == 0.0
    assert len(t_check["subtasks"]) == 2

    # Complete Step 1
    patch_s1 = client.patch(
        f"/api/v1/todos/{todo_id}/subtasks/{s1['id']}", json={"is_completed": True}
    )
    assert patch_s1.status_code == 200
    assert patch_s1.json()["is_completed"] == True

    # Progress should now be 50%
    t_50 = client.get(f"/api/v1/todos/{todo_id}").json()
    assert t_50["subtasks_completed_count"] == 1
    assert t_50["progress_percentage"] == 50.0

    # Toggle Step 2 using toggle endpoint
    toggle_s2 = client.patch(f"/api/v1/todos/{todo_id}/subtasks/{s2['id']}/toggle")
    assert toggle_s2.status_code == 200
    assert toggle_s2.json()["is_completed"] == True

    # Progress should now be 100%
    t_100 = client.get(f"/api/v1/todos/{todo_id}").json()
    assert t_100["subtasks_completed_count"] == 2
    assert t_100["progress_percentage"] == 100.0

    # Delete Step 2
    del_s2 = client.delete(f"/api/v1/todos/{todo_id}/subtasks/{s2['id']}")
    assert del_s2.status_code == 200

    # Progress with 1 of 1 completed
    t_final = client.get(f"/api/v1/todos/{todo_id}").json()
    assert t_final["subtasks_count"] == 1
    assert t_final["subtasks_completed_count"] == 1
    assert t_final["progress_percentage"] == 100.0


def test_is_completed_query_filter(client: TestClient):
    """Verify filtering todos by is_completed boolean query parameter."""
    client.post("/api/v1/todos", json={"title": "Active 1", "status": "PENDING"})
    client.post("/api/v1/todos", json={"title": "Active 2", "status": "IN_PROGRESS"})
    client.post("/api/v1/todos", json={"title": "Done 1", "status": "COMPLETED"})

    # Filter active (not completed)
    active_res = client.get("/api/v1/todos?is_completed=false")
    assert active_res.status_code == 200
    for item in active_res.json()["items"]:
        assert item["is_completed"] is False
        assert item["status"] != "COMPLETED"

    # Filter completed
    done_res = client.get("/api/v1/todos?is_completed=true")
    assert done_res.status_code == 200
    for item in done_res.json()["items"]:
        assert item["is_completed"] is True
        assert item["status"] == "COMPLETED"


def test_analytics_productivity_stats(client: TestClient):
    """Verify GET /api/v1/analytics/stats returns comprehensive metrics."""
    client.post("/api/v1/todos", json={"title": "Task 1", "status": "COMPLETED", "priority": "HIGH"})
    client.post("/api/v1/todos", json={"title": "Task 2", "status": "PENDING", "priority": "LOW"})

    res = client.get("/api/v1/analytics/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_todos" in data
    assert data["total_todos"] >= 2
    assert "completed_todos" in data
    assert "completion_rate" in data
    assert "priority_breakdown" in data
    assert "category_breakdown" in data
    assert "subtasks_total" in data


def test_export_import_json_and_csv(client: TestClient):
    """Verify JSON and CSV export and JSON backup restore."""
    # 1. Create test data
    t = client.post("/api/v1/todos", json={"title": "Export Test Item", "priority": "URGENT"}).json()
    client.post(f"/api/v1/todos/{t['id']}/subtasks", json={"title": "Exported Subtask"})

    # 2. JSON Export
    json_exp = client.get("/api/v1/export/json")
    assert json_exp.status_code == 200
    backup = json_exp.json()
    assert "version" in backup
    assert "todos" in backup
    assert "categories" in backup
    assert "subtasks" in backup
    assert any(item["title"] == "Export Test Item" for item in backup["todos"])

    # 3. CSV Export
    csv_exp = client.get("/api/v1/export/csv")
    assert csv_exp.status_code == 200
    assert "text/csv" in csv_exp.headers["content-type"]
    assert "Export Test Item" in csv_exp.text
    assert "ID,Title,Description" in csv_exp.text

    # 4. JSON Import
    import_payload = {
        "categories": [{"name": "Imported Category", "color": "#E11D48"}],
        "todos": [
            {
                "id": 999,
                "title": "Restored From Backup",
                "priority": "HIGH",
                "status": "COMPLETED",
            }
        ],
        "subtasks": [
            {
                "todo_id": 999,
                "title": "Restored Checklist Item",
                "is_completed": True,
            }
        ],
    }
    imp_res = client.post("/api/v1/import/json", json=import_payload)
    assert imp_res.status_code == 201
    imp_data = imp_res.json()
    assert imp_data["imported_todos"] == 1
    assert imp_data["imported_subtasks"] == 1

    # Verify restored todo exists in database
    search_res = client.get("/api/v1/todos?search=Restored+From+Backup")
    assert search_res.status_code == 200
    assert search_res.json()["total"] >= 1
    restored_item = search_res.json()["items"][0]
    assert restored_item["title"] == "Restored From Backup"
    assert restored_item["is_completed"] is True
    assert restored_item["subtasks_count"] == 1
