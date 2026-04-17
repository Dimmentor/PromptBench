from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from src.core.database import Base
from src.domain.enums import RequestStatus


class Request(Base):
    __tablename__ = "requests"

    test_id = mapped_column(
        ForeignKey("tests.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[RequestStatus] = mapped_column(default=RequestStatus.PENDING)

    test = relationship("Test", back_populates="requests")
    response = relationship("Response", back_populates="request", uselist=False)