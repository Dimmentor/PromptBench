from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src.application.services.gateway_app_service import GatewayApplicationService
from src.infrastructure.di import get_gateway_application_service
from src.interfaces.schemas.gateway import GatewayBatchItem

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.post("/batch/stream")
async def gateway_batch_stream(
    items: list[GatewayBatchItem],
    svc: GatewayApplicationService = Depends(get_gateway_application_service),
):
    async def gen():
        async for chunk in svc.stream_batch_sse(items):
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")

