from typing import Optional

from redis.asyncio import Redis


class RedisCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get_from_cache(self, cache_key: str) -> Optional[str]:
        value = await self.redis.get(cache_key)
        if value:
            return value.decode("utf-8")
        return None

    async def store_in_cache(self, cache_key: str, value: str):
        await self.redis.set(cache_key, value)

    async def increment_view_count(
        self, short_key: str, initial_views: int = 0, threshold: int = 10
    ) -> int:
        views_key = f"views:{short_key}"
        views = await self.redis.get(views_key)
        new_views = int(views) + 1 if views else initial_views + 1

        await self.redis.set(views_key, new_views)
        return new_views

    async def get_view_count(self, short_key: str) -> Optional[int]:
        views = await self.redis.get(f"views:{short_key}")
        if views is not None:
            return int(views)
        return None
