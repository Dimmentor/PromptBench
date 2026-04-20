import os
from dataclasses import dataclass

from src.core.config import settings
from src.domain.enums import TestStatus, RequestStatus
from src.infrastructure.storage.fs_index import request_id_from_path


@dataclass(frozen=True)
class FsRequest:
    id: str
    test_id: str
    file_path: str
    status: str
    response_file_path: str | None = None
    response_error_path: str | None = None
    duration: int | None = None


def _test_dir(test_id: str) -> str:
    return os.path.join(settings.STORAGE, test_id)


def _requests_dir(test_id: str) -> str:
    return os.path.join(_test_dir(test_id), "requests")


def _responses_dir(test_id: str) -> str:
    return os.path.join(_test_dir(test_id), "responses")


def _running_marker(test_id: str) -> str:
    return os.path.join(_test_dir(test_id), ".running")


def list_test_ids() -> list[str]:
    if not os.path.exists(settings.STORAGE):
        return []
    return sorted(
        d for d in os.listdir(settings.STORAGE)
        if os.path.isdir(os.path.join(settings.STORAGE, d)) and not d.startswith(".")
    )


def list_request_files(test_id: str) -> list[str]:
    path = _requests_dir(test_id)
    if not os.path.exists(path):
        return []
    files = [
        os.path.join(path, f)
        for f in os.listdir(path)
        if f.endswith(".json") and os.path.isfile(os.path.join(path, f))
    ]
    return sorted(files)


def compute_request(test_id: str, request_file_path: str) -> FsRequest:
    rid = request_id_from_path(request_file_path)

    responses_dir = _responses_dir(test_id)
    ok_path = os.path.join(responses_dir, f"response_{rid}.json")
    err_path = os.path.join(responses_dir, f"response_{rid}.error.json")
    meta_path = os.path.join(responses_dir, f"response_{rid}.meta.json")

    if os.path.exists(err_path):
        status = RequestStatus.FAILED
        response_path = None
    elif os.path.exists(ok_path):
        status = RequestStatus.DONE
        response_path = ok_path
    else:
        status = RequestStatus.PENDING
        response_path = None

    duration = None
    if os.path.exists(meta_path):
        try:
            import json
            with open(meta_path, "r", encoding="utf-8") as f:
                duration = json.load(f).get("duration")
        except Exception:
            duration = None

    return FsRequest(
        id=rid,
        test_id=test_id,
        file_path=request_file_path,
        status=str(status),
        response_file_path=response_path,
        response_error_path=err_path if os.path.exists(err_path) else None,
        duration=duration,
    )


def get_test_status(test_id: str) -> str:
    if os.path.exists(_running_marker(test_id)):
        return str(TestStatus.RUNNING)

    request_files = list_request_files(test_id)
    if not request_files:
        return str(TestStatus.CREATED)

    failed = 0
    done = 0
    for rf in request_files:
        req = compute_request(test_id, rf)
        if req.status == str(RequestStatus.FAILED):
            failed += 1
        elif req.status == str(RequestStatus.DONE):
            done += 1

    if failed > 0:
        return str(TestStatus.FAILED)
    if done == len(request_files):
        return str(TestStatus.COMPLETED)
    return str(TestStatus.CREATED)


def get_progress(test_id: str) -> dict:
    request_files = list_request_files(test_id)
    total = len(request_files)
    done = 0
    failed = 0
    for rf in request_files:
        req = compute_request(test_id, rf)
        if req.status == str(RequestStatus.DONE):
            done += 1
        elif req.status == str(RequestStatus.FAILED):
            failed += 1
    return {"total": total, "done": done, "failed": failed, "pending": total - done - failed}

