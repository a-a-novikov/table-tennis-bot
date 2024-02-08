from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

db_engine = create_async_engine(
    settings.POSTGRES_DSN,
    echo=settings.DEBUG,
    isolation_level="AUTOCOMMIT",
    pool_pre_ping=True,
)

DBSessionFactory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор БД-сессии."""
    async with DBSessionFactory() as session:
        yield session
