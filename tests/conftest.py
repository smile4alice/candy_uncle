import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from src.database import Base, async_session_maker


DATABASE_URL_TEST = "postgresql+asyncpg://test_u:test_p@localhost:6999/test_db"


async def create_database():
    global engine_test
    engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
    Base.metadata.bind = engine_test
    async_session_maker.kw["bind"] = engine_test
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    await create_database()
    yield
    await drop_database()
