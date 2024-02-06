import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from dto import CoupleTourneyDTO, UserDTO, EnrichedUserDTO
from repositories.couple_tourney import CoupleTourneyRepository


class TooManyTourneys(Exception):
    pass


class ActiveTourneyNotFound(Exception):
    pass


class CoupleTourneyManager:
    def __init__(self, session: AsyncSession):
        self.repository: CoupleTourneyRepository = CoupleTourneyRepository(session)

    async def add_tourney(
        self,
        initiator_id: int,
        acceptor_id: int,
        wins_total: int,
        registered_at: datetime.date = datetime.date.today(),
    ) -> CoupleTourneyDTO:
        try:
            tourney = await self.repository.create_tourney(initiator_id, acceptor_id, wins_total, registered_at)
        except IntegrityError:
            raise TooManyTourneys()
        return CoupleTourneyDTO.from_db(tourney)

    async def get_active_tourney(self, initiator_or_acceptor_id: int) -> CoupleTourneyDTO | None:
        tourney = await self.repository.retrieve_active_tourney(initiator_or_acceptor_id)
        if not tourney:
            return None
        return CoupleTourneyDTO.from_db(tourney)

    async def update_active_tourney_score(self, winner_id: int) -> CoupleTourneyDTO:
        tourney = await self.repository.retrieve_active_tourney(winner_id)
        if not tourney:
            raise ActiveTourneyNotFound()
        tourney_dto = CoupleTourneyDTO.from_db(tourney)

        tourney_dto.games_played += 1
        if winner_id == tourney_dto.initiator_id:
            tourney_dto.initiator_wins += 1
        else:
            tourney_dto.acceptor_wins += 1

        updated_tourney = await self.repository.update_active_tourney(tourney_dto)
        return CoupleTourneyDTO.from_db(updated_tourney)

    async def accept_tourney(self, acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(acceptor_id)
        if not tourney:
            return None
        tourney_dto = CoupleTourneyDTO.from_db(tourney)
        tourney_dto.is_accepted = True
        await self.repository.update_active_tourney(tourney_dto)

    async def decline_tourney(self, acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(acceptor_id)
        if not tourney:
            return None
        tourney_dto = CoupleTourneyDTO.from_db(tourney)
        tourney_dto.is_finished = True
        await self.repository.update_active_tourney(tourney_dto)

    async def finish_tourney(self, initiator_or_acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(initiator_or_acceptor_id)
        if not tourney:
            return None
        tourney_dto = CoupleTourneyDTO.from_db(tourney)
        tourney_dto.is_finished = True
        await self.repository.update_active_tourney(tourney_dto)

    async def get_users_available_for_tourney(
        self,
        all_users: list[EnrichedUserDTO],
        author_id: int,
    ) -> list[EnrichedUserDTO]:
        available_users = []
        for u in all_users:
            if u.chat_id == author_id:
                continue
            active_tourney = await self.repository.retrieve_active_tourney(u.chat_id)
            if active_tourney:
                continue
            available_users.append(u)
        return available_users
