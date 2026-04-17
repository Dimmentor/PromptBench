from typing import List
from pydantic import BaseModel
from src.interfaces.schemas.request import RequestReadWithResponse


class TestCreate(BaseModel):
    name: str


class TestReadSimple(BaseModel):
    id: int
    name: str
    status: str


class TestRead(BaseModel):
    id: int
    name: str
    status: str
    requests: List[RequestReadWithResponse] = []


class ProgressResponse(BaseModel):
    total: int
    done: int
    failed: int
    pending: int