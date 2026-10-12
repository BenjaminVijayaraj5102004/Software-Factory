from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, text
from backend.app.core.config import settings
from backend.app.core.database import get_session

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check(session: Session = Depends(get_session)):
    """Health check probe verifying server and SQLite database readiness."""
    db_status = "connected"
    todos_count = 0
    categories_count = 0
    try:
        session.exec(text("SELECT 1")).first()
        todo_res = session.exec(text("SELECT COUNT(*) FROM todo")).first()
        if todo_res:
            todos_count = int(todo_res[0])
        cat_res = session.exec(text("SELECT COUNT(*) FROM category")).first()
        if cat_res:
            categories_count = int(cat_res[0])
    except Exception as exc:
        db_status = f"error: {str(exc)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": db_status},
        )

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "todos_count": todos_count,
        "categories_count": categories_count,
    }
