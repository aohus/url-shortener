import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from adapters.orm import metadata, start_mappers


@pytest.fixture(scope="session")
async def async_in_memory_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_in_memory_db):
    start_mappers()
    async_session_factory = sessionmaker(
        bind=async_in_memory_db, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
    clear_mappers()
