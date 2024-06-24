import asyncio
from datetime import datetime
from typing import Dict, Optional

import pytest

from adapters.cache import RedisCache
from adapters.repository import AbstractRepository
from domain import model
from service_layer.services import URLNotExist, URLService


@pytest.fixture
def fake_repo():
    return FakeRepository([])


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def cache(fake_redis):
    return RedisCache(fake_redis)


@pytest.fixture
def services(fake_repo, cache):
    return URLService(fake_repo, cache)


class FakeRedis:
    def __init__(self):
        self.storage: Dict[str, str] = {}
        self.expirations: Dict[str, int] = {}

    async def get(self, key: str) -> Optional[str]:
        if (
            key in self.expirations
            and self.expirations[key] < asyncio.get_event_loop().time()
        ):
            del self.storage[key]
            del self.expirations[key]
            return None
        return self.storage.get(key, None)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        self.storage[key] = str(value).encode("utf-8")
        if ex is not None:
            self.expirations[key] = asyncio.get_event_loop().time() + ex

    async def expire(self, key: str, ex: int):
        if key in self.storage:
            self.expirations[key] = asyncio.get_event_loop().time() + ex

    async def delete(self, key: str):
        if key in self.storage:
            del self.storage[key]
        if key in self.expirations:
            del self.expirations[key]

    async def incr(self, key: str):
        if key in self.storage:
            self.storage[key] = str(int(self.storage[key]) + 1)
        else:
            self.storage[key] = "1"
        return int(self.storage[key])

    async def pipeline(self, transaction: bool = True):
        return self

    async def execute(self):
        # In real redis, this executes all commands in the pipeline.
        # In this fake version, commands are executed immediately.
        pass


class FakeRepository(AbstractRepository):
    def __init__(self, urls):
        self._urls = list(urls)

    async def get(self, **kwargs):
        for key, value in kwargs.items():
            if key in ("original_url", "short_key"):
                url_data = [
                    e
                    for e in self._urls
                    if getattr(e, key) == value
                    and (e.expired_at is None or e.expired_at > datetime.utcnow())
                ]
                if url_data:
                    return url_data[0]
                return None
        raise ValueError("No valid key found in kwargs")

    async def add(self, url: model.URL):
        self._urls.append(url)

    async def update(self, url: model.URL) -> model.URL:
        for i, existing_url in enumerate(self._urls):
            if existing_url.short_key == url.short_key:
                self._urls[i] = url
                return url
        raise ValueError("URL not found")

    async def list(self):
        return self._urls


class FakeSession:
    committed = False

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_generate_short_key(services):
    original_url = "https://www.example.com"
    expired_at = datetime.strptime("2024-12-31", "%Y-%m-%d")
    short_key = await services.generate_short_key(original_url, expired_at)
    assert short_key is not None


@pytest.mark.asyncio
async def test_generate_short_key_if_expired_at_none(services):
    original_url = "https://www.example.com"
    expired_at = None
    short_key = await services.generate_short_key(original_url, expired_at)
    assert short_key is not None


@pytest.mark.asyncio
async def test_return_short_key_already_exist(fake_repo, services):
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    expired_at = None
    new_url = model.URL(original_url=original_url, short_key=short_key, expired_at=None)
    await fake_repo.add(new_url)
    short_key_response = await services.generate_short_key(original_url, expired_at)
    assert short_key == short_key_response
    assert len(await fake_repo.list()) == 1


@pytest.mark.asyncio
async def test_get_original_url(fake_repo, services):
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    new_url = model.URL(original_url=original_url, short_key=short_key, expired_at=None)
    await fake_repo.add(new_url)
    original_url_response = await services.get_original_url(short_key)
    assert original_url == original_url_response


@pytest.mark.asyncio
async def test_get_original_url_if_not_exist(fake_repo, services):
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    new_url = model.URL(original_url=original_url, short_key=short_key, expired_at=None)
    await fake_repo.add(new_url)

    with pytest.raises(URLNotExist):
        await services.get_original_url("ABC123")


@pytest.mark.asyncio
async def test_get_original_url_after_expired(fake_repo, services):
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    expired_at = datetime.strptime("2024-06-10", "%Y-%m-%d")
    new_url = model.URL(
        original_url=original_url, short_key=short_key, expired_at=expired_at
    )
    await fake_repo.add(new_url)

    assert (await fake_repo.list())[0].short_key == short_key
    with pytest.raises(URLNotExist):
        await services.get_original_url(short_key)


@pytest.mark.asyncio
async def test_get_view_count(fake_repo, services):
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    new_url = model.URL(original_url=original_url, short_key=short_key, expired_at=None)
    await fake_repo.add(new_url)

    # view 4 times
    await services.get_original_url(short_key)
    await services.get_original_url(short_key)
    await services.get_original_url(short_key)
    await services.get_original_url(short_key)
    assert await services.get_view_count(short_key) == 4
