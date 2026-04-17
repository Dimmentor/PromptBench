from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.response import Response


class ResponseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, request_id: int, file_path: str, duration: int | None = None) -> Response:
        response = Response(request_id=request_id, file_path=file_path, duration=duration)
        self.session.add(response)
        await self.session.commit()
        await self.session.refresh(response)
        return response
