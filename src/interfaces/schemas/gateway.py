from typing import Any
from pydantic import BaseModel, Field


class GatewayBatchItem(BaseModel):
    id: str | int = Field(..., description="Client-provided correlation id")
    payload: dict[str, Any] = Field(..., description="OpenAI-like request payload for orchestrator")