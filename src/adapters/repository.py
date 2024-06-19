import abc
import logging
from typing import Any, Optional

from domain import model
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# 데이터베이스 설정
DATABASE_URL = "sqlite:///./url_shortener.db"
engine = create_engine(DATABASE_URL)


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def get(self, **kwargs: dict[str, Any]) -> model.URL:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, **kwargs: dict[str, Any]) -> model.URL:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_key(self, key: str, value: Any) -> model.URL:
        result = (
            self.session.query(model.URL)
            .filter(getattr(model.URL, key) == value)
            .first()
        )
        logging.info(result)
        return result

    def get(self, **kwargs: dict[str, Any]) -> model.URL:
        for key, value in kwargs.items():
            if hasattr(model.URL, key):
                return self.get_by_key(key, value)
        raise ValueError("No valid key found in kwargs")

    def add(self, **kwargs: dict[str, Any]) -> model.URL:
        url_data = {
            key: value for key, value in kwargs.items() if hasattr(model.URL, key)
        }
        if not url_data:
            raise ValueError("No valid data provided to create a URL object")

        new_url = model.URL(**url_data)
        self.session.add(new_url)
        self.session.commit()
        self.session.refresh(new_url)
        return new_url
