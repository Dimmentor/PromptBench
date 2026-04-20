import json
import os
import shutil


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

    async def list_dirs(self, path: str) -> list[str]:
        if not os.path.exists(path):
            return []
        return [
            os.path.join(path, d)
            for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")
        ]

    async def exists(self, path: str) -> bool:
        return os.path.exists(path)

    async def touch(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8"):
            pass

    async def remove_file(self, path: str):
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(path)

    async def remove_tree(self, path: str):
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)