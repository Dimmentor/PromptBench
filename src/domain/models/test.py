from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from src.core.database import Base
from src.domain.enums import TestStatus


class Test(Base):
    __tablename__ = "tests"

    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[TestStatus] = mapped_column(default=TestStatus.CREATED)
    storage_path: Mapped[str] = mapped_column(String(500))

    requests = relationship(
        "Request",
        back_populates="test",
        cascade="all, delete-orphan"
    )