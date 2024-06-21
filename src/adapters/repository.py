import abc
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from domain import model


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    async def get(self, **kwargs: dict[str, Any]) -> model.URL:
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, **kwargs: dict[str, Any]) -> model.URL:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, **kwargs: dict[str, Any]) -> Optional[model.URL]:
        for key, value in kwargs.items():
            if hasattr(model.URL, key):
                query = select(model.URL).filter(
                    getattr(model.URL, key) == value,
                    (
                        model.URL.expired_at.is_(None)
                        | (model.URL.expired_at > datetime.utcnow())
                    ),
                )
                result = await self.session.execute(query)
                return result.scalars().first()
        raise ValueError("No valid key found in kwargs")

    async def add(self, url: model.URL):
        self.session.add(url)
        await self.session.commit()
        await self.session.refresh(url)

    async def update(self, url: model.URL):
        await self.session.commit()
        await self.session.refresh(url)
        return url
