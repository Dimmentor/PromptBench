import os
import re
import time
import uuid


_INVALID_CHARS = re.compile(r"[^a-zA-Z0-9._ -]+")


def safe_dirname(name: str) -> str:
    cleaned = _INVALID_CHARS.sub("", name).strip().replace(" ", "_")
    cleaned = cleaned.strip("._-")
    return cleaned or "test"


def unique_test_id(base_dir: str, requested_name: str) -> str:
    base = safe_dirname(requested_name)
    candidate = base
    if not os.path.exists(os.path.join(base_dir, candidate)):
        return candidate

    suffix = uuid.uuid4().hex[:8]
    candidate = f"{base}_{suffix}"
    if not os.path.exists(os.path.join(base_dir, candidate)):
        return candidate

    candidate = f"{base}_{int(time.time())}_{suffix}"
    return candidate


def unique_request_id() -> str:
    # Request id is used in filename, so keep it filesystem-safe.
    return uuid.uuid4().hex[:16]


def request_id_from_path(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]

