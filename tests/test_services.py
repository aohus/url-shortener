from datetime import datetime

import pytest
from adapters import repository
from domain import model
from service_layer import services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, url):
        self._url = list(url)

    def add(self, **kwargs):
        url_data = {
            key: value
            for key, value in kwargs.items()
            if key
            in ("original_url", "short_key", "created_at", "modified_at", "expired_at")
        }
        self._url.append(url_data)

    def get(self, **kwargs):
        for key, value in kwargs.items():
            if key in ("original_url", "short_key"):
                url_data = [
                    e
                    for e in self._url
                    if e.get(key) == value
                    and (
                        e.get("expired_at") is None
                        or e.get("expired_at") > datetime.utcnow()
                    )
                ]
                if url_data:
                    return model.URL(**url_data[0])
                return None
        raise ValueError("No valid key found in kwargs")

    def list(self):
        return self._url


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_generate_short_key():
    repo = FakeRepository([])
    original_url = "https://www.example.com"
    expired_at = datetime.strptime("2024-12-31", "%Y-%m-%d")
    short_key = services.generate_short_key(original_url, expired_at, repo)
    assert short_key is not None


def test_generate_short_key_if_expired_at_none():
    repo = FakeRepository([])
    original_url = "https://www.example.com"
    expired_at = None
    short_key = services.generate_short_key(original_url, expired_at, repo)
    assert short_key is not None


def test_return_short_key_already_exist():
    repo = FakeRepository([])
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    expired_at = None
    repo.add(original_url=original_url, short_key=short_key, expired_date=None)
    short_key_response = services.generate_short_key(original_url, expired_at, repo)
    assert short_key == short_key_response
    assert len(repo.list()) == 1


def test_get_original_url():
    repo = FakeRepository([])
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    repo.add(original_url=original_url, short_key=short_key, expired_date=None)
    original_url_response = services.get_original_url(short_key, repo)
    assert original_url == original_url_response


def test_get_original_url_if_not_exist():
    repo = FakeRepository([])
    original_url = "https://www.example.com"
    short_key = "XYZ123"
    repo.add(original_url=original_url, short_key=short_key, expired_date=None)

    with pytest.raises(services.URLNotExist):
        services.get_original_url("ABC123", repo)
