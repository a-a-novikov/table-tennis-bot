import datetime

from sqlalchemy import select

from db.models import AfterDailyBooking
from repositories.base import BaseRepository


class AfterDailyBookingRepository(BaseRepository):

    async def create_booking(self, chat_id: int, date: datetime.date) -> AfterDailyBooking:
        booking = AfterDailyBooking(user_id=chat_id, date=date)
        self.session.add(booking)
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def retrieve_booking(self, chat_id: int, date: datetime.date) -> AfterDailyBooking | None:
        booking = await self.session.get(AfterDailyBooking, (chat_id, date))
        return booking

    async def retrieve_all_bookings_for_day(self, date: datetime.date) -> list[AfterDailyBooking]:
        booking_query = await self.session.execute(
            select("*").select_from(AfterDailyBooking).where(AfterDailyBooking.date == date)
        )
        return [AfterDailyBooking(**b) for b in booking_query.mappings().all()]

    async def update_booking(self, chat_id: int, date: datetime.date, win: bool) -> AfterDailyBooking:
        booking = await self.retrieve_booking(chat_id=chat_id, date=date)
        booking.win = win
        self.session.add(booking)
        await self.session.commit()
        return booking

    async def delete_booking(self, chat_id: int, date: datetime.date) -> None:
        booking = await self.retrieve_booking(chat_id=chat_id, date=date)
        if not booking:
            return None
        await self.session.delete(booking)
        await self.session.commit()
