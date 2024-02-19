import dataclasses
import datetime
from typing import Self

from db.models import User, AfterDailyBooking, CoupleTourney


@dataclasses.dataclass
class UserDTO:
    chat_id: int

    @classmethod
    def from_db(cls, instance: User) -> Self:
        return UserDTO(
            chat_id=instance.chat_id,
        )


@dataclasses.dataclass
class EnrichedUserDTO:
    chat_id: int
    username: str
    first_name: str | None
    last_name: str | None


@dataclasses.dataclass
class AfterDailyBookingDTO:
    user_id: int
    date: datetime.date
    win: bool | None = None

    @classmethod
    def from_db(cls, instance: AfterDailyBooking) -> Self:
        return AfterDailyBookingDTO(
            user_id=instance.user_id,
            date=instance.date,
            win=instance.win,
        )

    def __hash__(self):
        return hash((self.user_id, self.date))

    def __eq__(self, other):
        return self.user_id == other.user_id and self.date == other.date

    def __lt__(self, other):
        return self.user_id < other.user_id or self.date < other.date


@dataclasses.dataclass
class CoupleTourneyDTO:
    initiator_id: int
    acceptor_id: int
    registered_at: datetime.datetime
    is_accepted: bool
    wins_total: int
    games_played: int
    initiator_wins: int
    acceptor_wins: int
    is_finished: bool

    @classmethod
    def from_db(cls, instance: CoupleTourney) -> Self:
        return CoupleTourneyDTO(
            initiator_id=instance.initiator_id,
            acceptor_id=instance.acceptor_id,
            registered_at=instance.registered_at,
            is_accepted=instance.is_accepted,
            wins_total=instance.wins_total,
            games_played=instance.games_played,
            initiator_wins=instance.initiator_wins,
            acceptor_wins=instance.acceptor_wins,
            is_finished=instance.is_finished,
        )


@dataclasses.dataclass
class UserStatisticsDTO:
    chat_id: int
    last_daily_game_date: datetime.date | None
    daily_wins: int
    daily_total: int
    couple_tourney_games_won: int
    couple_tourney_games_total: int
    couple_tourney_won: int
    couple_tourney_total: int
