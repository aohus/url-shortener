from datetime import datetime
from typing import Optional

from adapters.repository import SqlAlchemyRepository
from domain import model


class URLNotExist(Exception):
    pass


def generate_short_key(
    original_url: str, expired_at: Optional[datetime], repo: SqlAlchemyRepository
):
    result = repo.get(original_url=original_url)
    if result:
        return result.short_key
    short_key = model.generate_short_key(original_url, expired_at, repo)
    return short_key


def get_original_url(short_key: str, repo: SqlAlchemyRepository):
    result = repo.get(short_key=short_key)
    if result:
        return result.original_url
    raise URLNotExist(f"no url for short key '{short_key}'")
