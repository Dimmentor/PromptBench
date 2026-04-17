from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import RequestStatus
from src.domain.models.request import Request


class RequestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, test_id: int, file_path: str) -> Request:
        req = Request(test_id=test_id, file_path=file_path)
        self.session.add(req)
        await self.session.commit()
        await self.session.refresh(req)
        return req

    async def mark_done(self, request_id: int):
        req = await self.session.get(Request, request_id)
        req.status = RequestStatus.DONE
        await self.session.commit()

    async def mark_failed(self, request_id: int):
        req = await self.session.get(Request, request_id)
        req.status = RequestStatus.FAILED
        await self.session.commit()
