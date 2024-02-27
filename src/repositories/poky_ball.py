import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db.models import PokyBall
from dto import PokyBallDTO
from repositories.base import BaseRepository


class PokyWithTheEmojiAlreadyExists(Exception):
    pass


class PokyBallNotFound(Exception):
    pass


class PokyBallRepository(BaseRepository):

    async def create_poky_ball(self, owner_id: int, emoji: str) -> PokyBallDTO:
        ball = PokyBall(owner_id=owner_id, emoji=emoji)
        self.session.add(ball)
        try:
            await self.session.commit()
        except IntegrityError:
            raise PokyWithTheEmojiAlreadyExists
        await self.session.refresh(ball)
        return PokyBallDTO.from_db(ball)

    async def retrieve_poky_ball(self, id_: int) -> PokyBallDTO | None:
        ball = await self.__retrieve_poky_ball(id_)
        return PokyBallDTO.from_db(ball)

    async def __retrieve_poky_ball(self, id_: int) -> PokyBall | None:
        ball = await self.session.get(PokyBall, id_)
        return ball

    async def retrieve_all_poky_balls_of_owner(self, owner_id: int) -> list[PokyBallDTO]:
        balls_query = await self.session.execute(
            select("*").select_from(PokyBall).where(PokyBall.owner_id == owner_id)
        )
        return [PokyBallDTO(**b) for b in balls_query.mappings().all()]

    async def update_poky_ball_owner(self, owner_id: int, id_: int) -> PokyBallDTO:
        ball = await self.__retrieve_poky_ball(id_)
        if not ball:
            raise PokyBallNotFound
        ball.owner_id = owner_id
        ball.ownership_since = datetime.date.today()
        self.session.add(ball)
        await self.session.commit()
        return PokyBallDTO.from_db(ball)
