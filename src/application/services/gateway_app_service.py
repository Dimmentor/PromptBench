import json
from collections.abc import AsyncIterator
from typing import Any

from src.interfaces.schemas.gateway import GatewayBatchItem


class GatewayApplicationService:
    """Orchestrator gateway use-cases (streaming batch, etc.)."""

    def __init__(self, llm_client: Any):
        self._llm = llm_client

    async def stream_batch_sse(self, items: list[GatewayBatchItem]) -> AsyncIterator[str]:
        for item in items:
            try:
                resp = await self._llm.send(dict(item.payload))
                data: dict[str, Any] = {"id": item.id, "payload": resp}
            except Exception as e:
                data = {
                    "id": item.id,
                    "error": {
                        "message": "Orchestrator request failed",
                        "details": str(e),
                    },
                }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
