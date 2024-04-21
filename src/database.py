from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import SETTINGS


engine = create_async_engine(url=SETTINGS.SQL_DSN, echo=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    creation_date: Mapped[datetime] = mapped_column(server_default=func.now())
    modification_date: Mapped[datetime] = mapped_column(onupdate=func.now())
