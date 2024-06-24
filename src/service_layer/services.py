from datetime import datetime
from typing import Optional

from adapters.cache import RedisCache
from adapters.repository import SqlAlchemyRepository
from domain.model import URL, IdGenerator, encode_base62


class URLNotExist(Exception):
    pass


class URLService:
    def __init__(self, repo: SqlAlchemyRepository, cache: RedisCache, node_id: int = 1):
        self.repo = repo
        self.cache = cache
        self.generator = IdGenerator(node_id)
        self.view_update_threshold = 10  # Define an update threshold

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
        original_url = await self.cache.get_from_cache(f"url:{short_key}")
        if original_url:
            new_views = await self.cache.increment_view_count(short_key)
            if new_views % self.view_update_threshold == 0:
                result = await self.repo.get(short_key=short_key)
                if result:
                    result.views = new_views
                    await self.repo.update(result)
            return original_url

        result = await self.repo.get(short_key=short_key)
        if result:
            await self.cache.store_in_cache(f"url:{short_key}", result.original_url)
            new_views = await self.cache.increment_view_count(short_key, result.views)
            if new_views % self.view_update_threshold == 0:
                result.views = new_views
                await self.repo.update(result)
            return result.original_url

        raise URLNotExist(f"No URL found for short key '{short_key}'")

    async def get_view_count(self, short_key: str) -> int:
        views = await self.cache.get_view_count(short_key)
        if views is not None:
            return views

        result = await self.repo.get(short_key=short_key)
        if result:
            await self.cache.store_in_cache(f"views:{short_key}", str(result.views))
            return result.views

        raise URLNotExist(f"No URL found for short key '{short_key}'")
