import json
import os


class LocalStorageService:
    async def save_json(self, path: str, data: dict):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def read_json(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def list_files(self, path: str) -> list[str]:
        if not os.path.exists(path):
            return []
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(".json")
        ]