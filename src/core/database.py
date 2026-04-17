from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, TIMESTAMP, func, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from src.core.logger import logger

DATABASE_URL = 'sqlite+aiosqlite:///db.sqlite3'

engine = create_async_engine(url=DATABASE_URL)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session():
    async with SessionLocal() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


async def check_connection():
    try:
        async with engine.begin() as conn:
            result = await conn.scalar(select(1))
            if result:
                logger.info("✅ SQLite connection successful")
        return True
    except Exception as e:
        logger.info(f"❌ SQLite connection error: {e}")
        return False
