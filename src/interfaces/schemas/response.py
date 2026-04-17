from pydantic import BaseModel


class ResponseRead(BaseModel):
    id: int
    request_id: int
    file_path: str
    duration: int | None
