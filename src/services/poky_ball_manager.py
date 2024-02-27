from sqlalchemy.ext.asyncio.session import AsyncSession

from dto import PokyBallDTO
from repositories.poky_ball import PokyBallRepository


class PokyBallManager:
    def __init__(self, session: AsyncSession):
        self.repository: PokyBallRepository = PokyBallRepository(session)

    async def add_poky_ball(
        self,
        owner_id: int,
        emoji: str,
    ) -> PokyBallDTO:
        return await self.repository.create_poky_ball(owner_id, emoji)

    async def get_poky_ball(self, id_: int) -> PokyBallDTO | None:
        return await self.repository.retrieve_poky_ball(id_)

    async def get_all_poky_balls_by_owner(self, owner_id: int) -> list[PokyBallDTO]:
        return await self.repository.retrieve_all_poky_balls_of_owner(owner_id)

    async def update_poky_ball_owner(self, owner_id: int, id_: int) -> PokyBallDTO:
        return await self.repository.update_poky_ball_owner(owner_id, id_)
