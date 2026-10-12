from datetime import datetime, timezone
from typing import Dict, List
from sqlalchemy import func
from sqlmodel import Session, select

from backend.app.models.enums import Priority, Status
from backend.app.models.todo import Todo
from backend.app.models.category import Category
from backend.app.models.subtask import Subtask
from backend.app.schemas.analytics import AnalyticsStats, CategoryBreakdown


class AnalyticsService:
    @classmethod
    def get_stats(cls, session: Session) -> AnalyticsStats:
        """Compute aggregated productivity stats and metrics."""
        now = datetime.now(timezone.utc)

        # Fetch all todos
        todos = session.exec(select(Todo)).all()
        total_todos = len(todos)

        completed_todos = 0
        pending_todos = 0
        in_progress_todos = 0
        overdue_todos = 0

        priority_breakdown: Dict[str, int] = {p.value: 0 for p in Priority}

        for t in todos:
            # Status counts
            if t.status == Status.COMPLETED:
                completed_todos += 1
            elif t.status == Status.IN_PROGRESS:
                in_progress_todos += 1
            else:
                pending_todos += 1

            # Priority count
            p_val = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
            if p_val in priority_breakdown:
                priority_breakdown[p_val] += 1
            else:
                priority_breakdown[p_val] = 1

            # Overdue calculation
            if t.due_date and t.status != Status.COMPLETED:
                due = t.due_date
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                if due < now:
                    overdue_todos += 1

        completion_rate = (
            round((completed_todos / total_todos) * 100.0, 1) if total_todos > 0 else 0.0
        )

        # Category breakdown
        categories = session.exec(select(Category)).all()
        category_breakdown: List[CategoryBreakdown] = []
        for cat in categories:
            cat_count = sum(1 for t in todos if t.category_id == cat.id)
            category_breakdown.append(
                CategoryBreakdown(
                    category_id=cat.id,
                    name=cat.name,
                    count=cat_count,
                    color=cat.color or "#6366f1",
                )
            )

        # Subtask stats
        subtasks = session.exec(select(Subtask)).all()
        subtasks_total = len(subtasks)
        subtasks_completed = sum(1 for st in subtasks if st.is_completed)
        subtask_completion_rate = (
            round((subtasks_completed / subtasks_total) * 100.0, 1)
            if subtasks_total > 0
            else 0.0
        )

        return AnalyticsStats(
            total_todos=total_todos,
            completed_todos=completed_todos,
            pending_todos=pending_todos,
            in_progress_todos=in_progress_todos,
            overdue_todos=overdue_todos,
            completion_rate=completion_rate,
            priority_breakdown=priority_breakdown,
            category_breakdown=category_breakdown,
            subtasks_total=subtasks_total,
            subtasks_completed=subtasks_completed,
            subtask_completion_rate=subtask_completion_rate,
        )
