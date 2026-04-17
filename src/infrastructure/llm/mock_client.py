import asyncio


class MockLLMClient:
    async def send(self, payload: dict) -> dict:
        await asyncio.sleep(0.1)
        return {
            "model": "qwen2.5:32b",
            "message": {
                "role": "assistant",
                "content": "Пример ответа от LLM...",
            },
            "done": True,
            "total_duration": 850000000,
        }