from db.models import User, AfterDailyBooking, CoupleTourney
from dto import UserDTO, UserStatisticsDTO

from repositories.base import BaseRepository
from sqlalchemy import select, or_, func


class UserRepository(BaseRepository):

    async def create_user(self, data: UserDTO) -> UserDTO:
        user = User(**data.__dict__)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserDTO.from_db(user)

    async def retrieve_user(self, chat_id: int) -> UserDTO | None:
        user = await self.__retrieve_user(chat_id)
        if not user:
            return None
        return UserDTO.from_db(user)

    async def __retrieve_user(self, chat_id: int) -> User | None:
        user = await self.session.get(User, chat_id)
        if user.deleted:
            return None
        return None

    async def retrieve_all_users(self) -> list[UserDTO] | None:
        users_query = await self.session.execute(select("*").select_from(User).where(User.deleted.is_(False)))
        return [UserDTO(**u) for u in users_query.mappings().all()]

    async def update_user(self, data: UserDTO) -> UserDTO | None:
        user = await self.__retrieve_user(chat_id=data.chat_id)
        if not user:
            return None
        user.title_poky_id = data.title_poky_id
        user.deleted = data.deleted
        self.session.add(user)
        await self.session.commit()
        return UserDTO.from_db(user)

    async def get_user_statistics(self, chat_id: int) -> UserStatisticsDTO | None:
        query = (
            select(
                User.chat_id,
                func.max(AfterDailyBooking.date).label("last_daily_game_date"),
                func.count(AfterDailyBooking.date.distinct()).filter(AfterDailyBooking.win.is_(True)).label("daily_wins"),
                func.count(AfterDailyBooking.date.distinct()).filter(AfterDailyBooking.win.is_not(None)).label("daily_total"),
                (
                    func.coalesce(func.sum(CoupleTourney.initiator_wins.distinct()).filter(CoupleTourney.initiator_id == chat_id), 0) +
                    func.coalesce(func.sum(CoupleTourney.acceptor_wins.distinct()).filter(CoupleTourney.acceptor_id == chat_id), 0)
                ).label("couple_tourney_games_won"),
                (
                        func.coalesce(func.sum(CoupleTourney.games_played.distinct()).filter(CoupleTourney.initiator_id == chat_id), 0) +
                        func.coalesce(func.sum(CoupleTourney.games_played.distinct()).filter(CoupleTourney.acceptor_id == chat_id,), 0)
                ).label("couple_tourney_games_total"),
                (
                    func.coalesce(func.count(CoupleTourney.registered_at.distinct()).filter(CoupleTourney.initiator_id == chat_id, CoupleTourney.initiator_wins == CoupleTourney.wins_total), 0) +
                    func.coalesce(func.count(CoupleTourney.registered_at.distinct()).filter(CoupleTourney.acceptor_id == chat_id, CoupleTourney.acceptor_wins == CoupleTourney.wins_total), 0)
                ).label("couple_tourney_won"),
                func.count(CoupleTourney.registered_at.distinct()).label("couple_tourney_total")
            )
            .select_from(User)
            .join(AfterDailyBooking, AfterDailyBooking.user_id == User.chat_id, isouter=True)
            .join(
                CoupleTourney,
                or_(
                    CoupleTourney.initiator_id == chat_id,
                    CoupleTourney.acceptor_id == chat_id,
                ),
                isouter=True,
            )
            .where(User.chat_id == chat_id)
            .group_by(User.chat_id)
        )
        result = await self.session.execute(query)
        mapped_result = result.mappings().one_or_none()
        if not mapped_result:
            return None
        return UserStatisticsDTO(**mapped_result)
