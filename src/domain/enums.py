from enum import Enum


class TestStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RequestStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DONE = "done"
    FAILED = "failed"