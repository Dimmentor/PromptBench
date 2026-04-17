from typing import List

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models.test import Test
from src.domain.models.request import Request
from src.domain.enums import RequestStatus


class TestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, storage_path: str) -> Test:
        test = Test(name=name, storage_path=storage_path)
        self.session.add(test)
        await self.session.commit()
        await self.session.refresh(test)
        return test

    async def get(self, test_id: int) -> Test | None:
        result = await self.session.execute(select(Test).where(Test.id == test_id))
        return result.scalar_one_or_none()

    async def get_with_requests(self, test_id: int) -> Test | None:
        result = await self.session.execute(
            select(Test)
            .options(selectinload(Test.requests).selectinload(Request.response))
            .where(Test.id == test_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[Test]:
        result = await self.session.execute(select(Test))
        return result.scalars().all()

    async def set_status(self, test_id: int, status: str):
        test = await self.get(test_id)
        test.status = status
        await self.session.commit()

    async def get_requests(self, test_id: int) -> List[Request]:
        result = await self.session.execute(
            select(Request).where(Request.test_id == test_id)
        )
        return result.scalars().all()

    async def get_progress(self, test_id: int) -> dict:
        result = await self.session.execute(
            select(
                func.count(Request.id),
                func.sum(
                    case(
                        (Request.status == RequestStatus.DONE, 1),
                        else_=0
                    )
                ),
                func.sum(
                    case(
                        (Request.status == RequestStatus.FAILED, 1),
                        else_=0
                    )
                ),
            ).where(Request.test_id == test_id)
        )

        total, done, failed = result.one()

        return {
            "total": total or 0,
            "done": done or 0,
            "failed": failed or 0,
            "pending": (total or 0) - (done or 0) - (failed or 0),
        }