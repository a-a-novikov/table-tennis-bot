from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class User(Base):
    __tablename__ = "user"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    title_poky_id: Mapped[int] = mapped_column(ForeignKey("poky_ball.id"), nullable=True)
    deleted: Mapped[bool] = mapped_column(server_default="false")

    title_poky: Mapped["PokyBall"] = relationship(
        back_populates="title_poky_balls", foreign_keys=[title_poky_id]
    )
    bookings: Mapped[list["AfterDailyBooking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    initiated_tourneys: Mapped[list["CoupleTourney"]] = relationship(
        back_populates="initiator",  foreign_keys="[CoupleTourney.initiator_id]",
    )
    accepted_tourneys: Mapped[list["CoupleTourney"]] = relationship(
        back_populates="acceptor", foreign_keys="[CoupleTourney.acceptor_id]",
    )
    poky_balls: Mapped[list["PokyBall"]] = relationship(
        back_populates="owner", foreign_keys="[PokyBall.owner_id]"
    )


class AfterDailyBooking(Base):
    __tablename__ = "after_daily_booking"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.chat_id"))
    date: Mapped[date] = mapped_column(Date())
    win: Mapped[Optional[bool]] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="bookings")

    __mapper_args__ = {"primary_key": [user_id, date]}


class CoupleTourney(Base):
    __tablename__ = "couple_tourney"
    __table_args__ = (
        Index("initiator_id_registered_at_idx", "initiator_id", "registered_at"),
    )

    initiator_id: Mapped[int] = mapped_column(ForeignKey("user.chat_id"))
    acceptor_id: Mapped[int] = mapped_column(ForeignKey("user.chat_id"))
    registered_at: Mapped[datetime] = mapped_column(DateTime())
    is_accepted: Mapped[bool] = mapped_column(default=False)
    wins_total: Mapped[int] = mapped_column()
    games_played: Mapped[int] = mapped_column(default=0)
    initiator_wins: Mapped[int] = mapped_column(default=0)
    acceptor_wins: Mapped[int] = mapped_column(default=0)
    is_finished: Mapped[bool] = mapped_column(default=False)

    initiator: Mapped["User"] = relationship(back_populates="initiated_tourneys", foreign_keys=[initiator_id])
    acceptor: Mapped["User"] = relationship(back_populates="accepted_tourneys", foreign_keys=[acceptor_id])

    __mapper_args__ = {"primary_key": [initiator_id, acceptor_id, registered_at]}


class PokyBall(Base):
    __tablename__ = "poky_ball"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    emoji: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.chat_id"), nullable=True)
    ownership_since: Mapped[date] = mapped_column(Date(), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="poky_balls", foreign_keys=[owner_id])
    title_poky_balls: Mapped[list["User"]] = relationship(
        back_populates="title_poky",  foreign_keys="[User.title_poky_id]",
    )
