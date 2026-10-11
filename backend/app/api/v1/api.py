import importlib
import logging
from fastapi import APIRouter
from backend.app.api.v1 import categories, health, todos

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Agent 1 Core Routes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(categories.router, tags=["Categories"])
api_router.include_router(todos.router, prefix="/todos", tags=["Todos"])

# Optional extension modules for Agent 2 and Agent 3
OPTIONAL_MODULES = [
    ("backend.app.api.v1.subtasks", "/todos", ["Subtasks"]),
    ("backend.app.api.v1.search", "/todos/search", ["Search"]),
    ("backend.app.api.v1.analytics", "/analytics", ["Analytics"]),
    ("backend.app.api.v1.export_import", "/data", ["Export & Import"]),
]

for mod_path, prefix, tags in OPTIONAL_MODULES:
    try:
        mod = importlib.import_module(mod_path)
        if hasattr(mod, "router"):
            api_router.include_router(mod.router, prefix=prefix, tags=tags)
            logger.info("Mounted extension router: %s at %s", mod_path, prefix)
    except ModuleNotFoundError:
        pass
    except Exception as exc:
        logger.warning("Could not mount extension router %s: %s", mod_path, exc)
