import os
from typing import List


class Settings:
    PROJECT_NAME: str = "Production Todo API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todo.db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS Origins (support dev & container setups)
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "*",
    ]
    BACKEND_CORS_ORIGINS: List[str] = CORS_ORIGINS


settings = Settings()
