import abc
from datetime import datetime
from typing import Any

from domain import model
from sqlalchemy.orm import Session


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

    def get(self, **kwargs: dict[str, Any]):
        for key, value in kwargs.items():
            if hasattr(model.URL, key):
                return (
                    self.session.query(model.URL)
                    .filter(
                        getattr(model.URL, key) == value,
                        (
                            model.URL.expired_at.is_(None)
                            | (model.URL.expired_at > datetime.utcnow())
                        ),
                    )
                    .first()
                )
        raise ValueError("No valid key found in kwargs")

    def add(self, url: model.URL):
        self.session.add(url)
        self.session.commit()
        self.session.refresh(url)

    def update(self, url: model.URL):
        self.session.commit()
        self.session.refresh(url)
        return url
