from typing import Any, Dict
from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.app.core.database import get_session
from backend.app.modules.export_import.export_import_service import ExportImportService

router = APIRouter()


@router.get("/export/json", summary="Export full database backup as JSON")
@router.get("/json", summary="Export full database backup as JSON (alias)")
def export_json(
    session: Session = Depends(get_session),
):
    """Download full backup containing all categories, todos, and subtasks."""
    data = ExportImportService.export_json(session=session)
    return data


@router.get("/export/csv", summary="Export todos as CSV file")
@router.get("/csv", summary="Export todos as CSV file (alias)")
def export_csv(
    session: Session = Depends(get_session),
):
    """Download todos list formatted as a CSV spreadsheet."""
    csv_content = ExportImportService.export_csv(session=session)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=todos.csv"},
    )


@router.post("/import/json", status_code=status.HTTP_201_CREATED, summary="Import todos from JSON backup")
@router.post("/json", status_code=status.HTTP_201_CREATED, summary="Import todos from JSON backup (alias)")
def import_json(
    payload: Dict[str, Any],
    session: Session = Depends(get_session),
):
    """Restore or import categories, todos, and subtasks from a JSON backup payload."""
    return ExportImportService.import_json(session=session, data=payload)
