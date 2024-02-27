import datetime

from sqlalchemy import select, or_, update
from sqlalchemy.exc import IntegrityError

from db.models import CoupleTourney
from dto import CoupleTourneyDTO
from repositories.base import BaseRepository


class TourneyExists(Exception):
    pass


class CoupleTourneyRepository(BaseRepository):

    async def create_tourney(
        self,
        initiator_id: int,
        acceptor_id: int,
        wins_total: int,
        registered_at: datetime.date,
    ) -> CoupleTourneyDTO:
        tourney = CoupleTourney(
            initiator_id=initiator_id,
            acceptor_id=acceptor_id,
            registered_at=registered_at,
            wins_total=wins_total,
        )
        self.session.add(tourney)
        try:
            await self.session.commit()
        except IntegrityError:
            raise TourneyExists
        await self.session.refresh(tourney)
        return CoupleTourneyDTO.from_db(tourney)

    async def retrieve_active_tourney(self, initiator_or_acceptor_id: int) -> CoupleTourneyDTO | None:
        query = select("*").select_from(CoupleTourney).where(
            or_(
                CoupleTourney.acceptor_id == initiator_or_acceptor_id,
                CoupleTourney.initiator_id == initiator_or_acceptor_id,
            ),
            CoupleTourney.is_finished.is_(False),
        )
        query_result = await self.session.execute(query)
        tourney_mapping = query_result.mappings().one_or_none()
        if not tourney_mapping:
            return None
        return CoupleTourneyDTO(**tourney_mapping)

    async def retrieve_tourney(
        self,
        initiator_id: int,
        acceptor_id: int,
        registered_at: datetime.date,
    ) -> CoupleTourneyDTO | None:
        tourney = await self.session.get(
            CoupleTourney,
            {
                "initiator_id": initiator_id,
                "acceptor_id": acceptor_id,
                "registered_at": registered_at,
            },
        )
        return CoupleTourneyDTO.from_db(tourney)

    async def update_active_tourney(self, data: CoupleTourneyDTO) -> CoupleTourneyDTO:
        query = update(CoupleTourney).where(
            CoupleTourney.initiator_id == data.initiator_id,
            CoupleTourney.acceptor_id == data.acceptor_id,
            CoupleTourney.is_finished.is_(False),
        ).values(
            is_accepted=data.is_accepted,
            games_played=data.games_played,
            initiator_wins=data.initiator_wins,
            acceptor_wins=data.acceptor_wins,
            is_finished=data.is_finished,
        )
        await self.session.execute(query)
        updated_tourney = await self.retrieve_tourney(
            data.initiator_id,
            data.acceptor_id,
            data.registered_at,
        )
        return updated_tourney
