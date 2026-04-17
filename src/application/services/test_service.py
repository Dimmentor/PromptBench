import os

from src.core.config import settings


class TestService:
    def __init__(self, repo):
        self.repo = repo

    async def create_test(self, name: str):
        # Create test first to get database ID
        test = await self.repo.create(name=name, storage_path="")

        # Use the database ID for directory naming
        base_path = os.path.join(settings.STORAGE, f"test_{test.id}")
        os.makedirs(os.path.join(base_path, "requests"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "responses"), exist_ok=True)

        # Update the test with the correct storage path
        test.storage_path = base_path
        await self.repo.session.commit()
        await self.repo.session.refresh(test)

        return test