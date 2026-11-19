from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    database: str = "postgresql"
    latency_ms: float | None = None
