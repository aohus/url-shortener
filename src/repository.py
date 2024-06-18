import abc
from typing import Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .model import URL

# 데이터베이스 설정
DATABASE_URL = "sqlite:///./url_shortener.db"
engine = create_engine(DATABASE_URL)


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def get(self, **kwargs: dict[str, Any]) -> Optional[URL]:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, **kwargs: dict[str, Any]) -> URL:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_key(self, key: str, value: Any) -> Optional[URL]:
        result = self.session.query(URL).filter(getattr(URL, key) == value).first()
        return result

    def get(self, **kwargs: dict[str, Any]) -> Optional[URL]:
        for key, value in kwargs.items():
            if hasattr(URL, key):
                return self.get_by_key(key, value)
        raise ValueError("No valid key found in kwargs")

    def add(self, **kwargs: dict[str, Any]) -> URL:
        url_data = {key: value for key, value in kwargs.items() if hasattr(URL, key)}
        if not url_data:
            raise ValueError("No valid data provided to create a URL object")

        new_url = URL(**url_data)
        self.session.add(new_url)
        self.session.commit()
        self.session.refresh(new_url)
        return new_url
