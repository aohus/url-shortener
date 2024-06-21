from datetime import datetime
from typing import Optional

from adapters.repository import SqlAlchemyRepository
from domain.model import URL, IdGenerator, encode_base62


class URLNotExist(Exception):
    pass


class URLService:
    def __init__(self, repo: SqlAlchemyRepository, node_id: int = 1):
        self.repo = repo
        self.generator = IdGenerator(node_id)

    async def generate_short_key(
        self, original_url: str, expired_at: Optional[datetime] = None
    ) -> str:
        result = await self.repo.get(original_url=original_url)
        if result:
            return result.short_key

        id = self.generator.generate_id()
        short_key = encode_base62(id)
        new_url = URL(
            original_url=original_url, short_key=short_key, expired_at=expired_at
        )
        await self.repo.add(new_url)
        return short_key

    async def get_original_url(self, short_key: str) -> str:
        result = await self.repo.get(short_key=short_key)
        if result:
            result.views += 1
            await self.repo.update(result)
            return result.original_url
        raise URLNotExist(f"No URL found for short key '{short_key}'")

    async def get_view_count(self, short_key: str) -> int:
        result = await self.repo.get(short_key=short_key)
        if result:
            return result.views
        raise URLNotExist(f"No URL found for short key '{short_key}'")
