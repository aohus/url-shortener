from datetime import datetime

import pytest

from adapters import repository
from domain import model
from service_layer.services import URLNotExist, URLService


@pytest.fixture
def fake_repo():
    return FakeRepository([])


@pytest.fixture
def services(fake_repo):
    return URLService(fake_repo)


class FakeRepository(repository.AbstractRepository):
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

    # view 3 times
    await services.get_original_url(short_key)
    await services.get_original_url(short_key)
    await services.get_original_url(short_key)

    assert await services.get_view_count(short_key) == 3
