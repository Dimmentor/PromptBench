from typing import Optional
from pydantic import BaseModel
from src.interfaces.schemas.response import ResponseRead


class RequestCreate(BaseModel):
    name: str | None = None
    payload: dict


class RequestRead(BaseModel):
    id: str
    test_id: str
    file_path: str
    status: str


class RequestReadWithResponse(BaseModel):
    id: str
    test_id: str
    file_path: str
    status: str
    response: Optional[ResponseRead] = None