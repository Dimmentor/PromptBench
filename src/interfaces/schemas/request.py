from typing import Optional
from pydantic import BaseModel
from src.interfaces.schemas.response import ResponseRead


class RequestCreate(BaseModel):
    payload: dict


class RequestRead(BaseModel):
    id: int
    test_id: int
    file_path: str
    status: str


class RequestReadWithResponse(BaseModel):
    id: int
    test_id: int
    file_path: str
    status: str
    response: Optional[ResponseRead] = None