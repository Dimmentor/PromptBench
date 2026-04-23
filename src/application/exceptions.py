"""Application-level errors mapped to HTTP by FastAPI exception handlers."""


class NotFoundError(Exception):
    def __init__(self, detail: str = "Not found"):
        self.detail = detail
        super().__init__(detail)
