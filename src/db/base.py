from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from src.config import settings
from sqlalchemy.orm import DeclarativeBase

db_engine = create_async_engine(
    settings.POSTGRES_DSN,
    echo=True,
    isolation_level="AUTOCOMMIT",
)

DBSessionFactory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор БД-сессии."""
    async with DBSessionFactory() as session:
        yield session
