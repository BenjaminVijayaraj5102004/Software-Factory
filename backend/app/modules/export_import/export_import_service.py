import csv
from datetime import datetime, timezone
import io
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select

from backend.app.models.category import Category
from backend.app.models.enums import Priority, Status
from backend.app.models.subtask import Subtask
from backend.app.models.todo import Todo
from backend.app.services.category_service import CategoryService


class ExportImportService:
    @classmethod
    def export_json(cls, session: Session) -> Dict[str, Any]:
        """Export all categories, todos, and subtasks as a complete JSON structure."""
        categories = session.exec(select(Category)).all()
        todos = session.exec(select(Todo)).all()
        subtasks = session.exec(select(Subtask)).all()

        return {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "color": c.color,
                    "icon": c.icon,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in categories
            ],
            "todos": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                    "status": t.status.value if hasattr(t.status, "value") else str(t.status),
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "tags": t.tags,
                    "category_id": t.category_id,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                }
                for t in todos
            ],
            "subtasks": [
                {
                    "id": st.id,
                    "todo_id": st.todo_id,
                    "title": st.title,
                    "is_completed": st.is_completed,
                    "created_at": st.created_at.isoformat() if st.created_at else None,
                }
                for st in subtasks
            ],
        }

    @classmethod
    def export_csv(cls, session: Session) -> str:
        """Export todos formatted as CSV spreadsheet string."""
        todos = session.exec(select(Todo)).all()
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "ID",
            "Title",
            "Description",
            "Priority",
            "Status",
            "Is Completed",
            "Due Date",
            "Tags",
            "Category ID",
            "Created At",
            "Completed At",
        ])

        for t in todos:
            p_val = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
            s_val = t.status.value if hasattr(t.status, "value") else str(t.status)
            is_completed = "Yes" if t.status == Status.COMPLETED else "No"
            writer.writerow([
                t.id,
                t.title,
                t.description or "",
                p_val,
                s_val,
                is_completed,
                t.due_date.isoformat() if t.due_date else "",
                t.tags or "",
                t.category_id or "",
                t.created_at.isoformat() if t.created_at else "",
                t.completed_at.isoformat() if t.completed_at else "",
            ])

        return output.getvalue()

    @classmethod
    def import_json(cls, session: Session, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore or import categories, todos, and subtasks from a JSON payload."""
        now = datetime.now(timezone.utc)
        imported_categories = 0
        imported_todos = 0
        imported_subtasks = 0

        # Mapping old IDs to new IDs
        cat_id_map: Dict[int, int] = {}
        todo_id_map: Dict[int, int] = {}

        # 1. Categories
        for cat_data in data.get("categories", []):
            name = cat_data.get("name", "").strip()
            if not name:
                continue
            cat = CategoryService.get_or_create(
                session,
                name=name,
                color=cat_data.get("color"),
                icon=cat_data.get("icon"),
            )
            old_id = cat_data.get("id")
            if old_id:
                cat_id_map[old_id] = cat.id
            imported_categories += 1

        # 2. Todos
        for t_data in data.get("todos", []):
            title = t_data.get("title", "").strip()
            if not title:
                continue

            # Priority parsing
            raw_p = t_data.get("priority", "MEDIUM").upper()
            priority = Priority[raw_p] if raw_p in Priority.__members__ else Priority.MEDIUM

            # Status parsing
            raw_s = t_data.get("status", "PENDING").upper()
            status = Status[raw_s] if raw_s in Status.__members__ else Status.PENDING

            # Due date parsing
            due_date = None
            if t_data.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(t_data["due_date"])
                except Exception:
                    pass

            old_cat_id = t_data.get("category_id")
            new_cat_id = cat_id_map.get(old_cat_id) if old_cat_id else None

            todo = Todo(
                title=title,
                description=t_data.get("description"),
                priority=priority,
                status=status,
                due_date=due_date,
                tags=t_data.get("tags"),
                category_id=new_cat_id,
                created_at=now,
                updated_at=now,
                completed_at=now if status == Status.COMPLETED else None,
            )
            session.add(todo)
            session.commit()
            session.refresh(todo)

            old_todo_id = t_data.get("id")
            if old_todo_id:
                todo_id_map[old_todo_id] = todo.id
            imported_todos += 1

        # 3. Subtasks
        for st_data in data.get("subtasks", []):
            title = st_data.get("title", "").strip()
            old_todo_id = st_data.get("todo_id")
            new_todo_id = todo_id_map.get(old_todo_id) if old_todo_id else None

            if not title or not new_todo_id:
                continue

            subtask = Subtask(
                title=title,
                is_completed=bool(st_data.get("is_completed", False)),
                todo_id=new_todo_id,
                created_at=now,
            )
            session.add(subtask)
            session.commit()
            imported_subtasks += 1

        return {
            "message": "Import completed successfully",
            "imported_categories": imported_categories,
            "imported_todos": imported_todos,
            "imported_subtasks": imported_subtasks,
        }
