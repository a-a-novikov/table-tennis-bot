from abc import ABC

from sqlalchemy.ext.asyncio.session import AsyncSession


class BaseRepository(ABC):

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
