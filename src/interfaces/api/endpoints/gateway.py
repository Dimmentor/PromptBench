import json
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from src.infrastructure.di import get_llm_client
from src.interfaces.schemas.gateway import GatewayBatchItem

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/batch/stream")
async def gateway_batch_stream(items: list[GatewayBatchItem]):

    llm = get_llm_client()

    async def gen():
        for item in items:
            try:
                resp = await llm.send(dict(item.payload))
                data = {"id": item.id, "payload": resp}
            except Exception as e:
                data = {"id": item.id, "error": {"message": "Orchestrator request failed", "details": str(e)}}

            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

