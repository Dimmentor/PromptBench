import asyncio
from typing import Any

import httpx

from src.core.config import settings


class OrchestratorLLMClient:
    """
    Client for Workshop Orchestrator (`/v1/chat/completions`).

    Important: Orchestrator is rate-limited/queued to 1 concurrent request by default.
    We also enforce a global semaphore on our side to keep test runs strictly sequential
    (across all running tests inside this backend process).
    """
    max_concurrent = settings.LLM_MAX_CONCURRENT_REQUESTS
    _global_semaphore = asyncio.Semaphore(max_concurrent)

    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None):
        self.base_url = (base_url or settings.ORCHESTRATOR_BASE_URL).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.ORCHESTRATOR_TIMEOUT_SECONDS

    async def send(self, payload: dict) -> dict:
        # Ensure non-streaming for now (we store final JSON response).
        if payload.get("stream") is None:
            payload = {**payload, "stream": False}

        url = f"{self.base_url}/v1/chat/completions"

        async with OrchestratorLLMClient._global_semaphore:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                try:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data: dict[str, Any] = resp.json()
                    return data
                except httpx.HTTPError as e:
                    # Make connection / HTTP errors debuggable in stored error file.
                    raise RuntimeError(f"Orchestrator request failed: {e} (url={url})") from e

