from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Response(Base):
    __tablename__ = "responses"

    request_id = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"))
    file_path: Mapped[str] = mapped_column(String(500))
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    request = relationship("Request", back_populates="response")