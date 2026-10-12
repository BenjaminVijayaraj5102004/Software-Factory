from typing import Optional
from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class DeleteResponse(BaseModel):
    ok: bool
    id: int
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    todos_count: Optional[int] = 0
    categories_count: Optional[int] = 0


# Alias for compatibility
HealthCheckResponse = HealthResponse
