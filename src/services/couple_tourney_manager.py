import datetime

from sqlalchemy.ext.asyncio.session import AsyncSession

from dto import CoupleTourneyDTO, EnrichedUserDTO
from repositories.couple_tourney import CoupleTourneyRepository


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
        return await self.repository.create_tourney(initiator_id, acceptor_id, wins_total, registered_at)

    async def get_active_tourney(self, initiator_or_acceptor_id: int) -> CoupleTourneyDTO | None:
        return await self.repository.retrieve_active_tourney(initiator_or_acceptor_id)

    async def update_active_tourney_score(self, winner_id: int) -> CoupleTourneyDTO:
        tourney = await self.repository.retrieve_active_tourney(winner_id)

        tourney.games_played += 1
        if winner_id == tourney.initiator_id:
            tourney.initiator_wins += 1
        else:
            tourney.acceptor_wins += 1

        if tourney.wins_total in (tourney.initiator_wins, tourney.acceptor_wins):
            tourney.is_finished = True
        updated_tourney = await self.repository.update_active_tourney(tourney)
        return updated_tourney

    async def accept_tourney(self, acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(acceptor_id)
        if not tourney:
            return None
        tourney.is_accepted = True
        await self.repository.update_active_tourney(tourney)

    async def decline_tourney(self, acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(acceptor_id)
        if not tourney:
            return None
        tourney.is_finished = True
        await self.repository.update_active_tourney(tourney)

    async def finish_tourney(self, initiator_or_acceptor_id: int) -> None:
        tourney = await self.repository.retrieve_active_tourney(initiator_or_acceptor_id)
        if not tourney:
            return None
        tourney.is_finished = True
        await self.repository.update_active_tourney(tourney)

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
