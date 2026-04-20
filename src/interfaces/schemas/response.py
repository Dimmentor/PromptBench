from pydantic import BaseModel


class ResponseRead(BaseModel):
    id: str
    request_id: str
    file_path: str
    duration: int | None
