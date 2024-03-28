import os
from subprocess import run as sp_run
from time import sleep

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from src.database import Base, async_session_maker


DATABASE_URL_TEST = "postgresql+asyncpg://test_u:test_p@localhost:6999/test_db"
DB_CONTAINER = "postgres_tests_uncle"
DB_VOLUME = f"{os.path.basename(os.getcwd())}_postgres_tests_data"


async def create_database():
    sp_run(["docker", "compose", "up", "postgres_tests", "-d"])
    while True:
        sleep(1)
        res = sp_run(
            [
                "docker",
                "inspect",
                "-f",
                "{{json .State.Health.Status}}",
                DB_CONTAINER,
            ],
            capture_output=True,
            text=True,
        )
        if "healthy" in res.stdout:
            break

    global engine_test
    engine_test = create_async_engine(
        DATABASE_URL_TEST,
        poolclass=NullPool,
    )

    Base.metadata.bind = engine_test
    async_session_maker.kw["bind"] = engine_test
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_database():
    print("DROP")
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    sp_run(["docker", "stop", DB_CONTAINER])
    sp_run(["docker", "rm", "-f", DB_CONTAINER])
    sp_run(["docker", "volume", "rm", DB_VOLUME])


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    await create_database()
    yield
    await drop_database()
