from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from db.base import DBSessionFactory


class DBSessionMiddleware(BaseMiddleware):
    """
    Мидлварь для передачи в конекст хэндлера БД-сессии SQLAlchemy.

    В контекст передается как "session".
    """
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        async with DBSessionFactory() as session:
            data["session"] = session
            return await handler(event, data)
