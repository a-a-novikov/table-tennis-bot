import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from dto import AfterDailyBookingDTO
from repositories.after_daily_booking import AfterDailyBookingRepository


class AfterDailyBookingManager:
    def __init__(self, session: AsyncSession):
        self.repository: AfterDailyBookingRepository = AfterDailyBookingRepository(session)

    async def add_booking(self, chat_id: int, date: datetime.date | None = None) -> AfterDailyBookingDTO:
        if not date:
            date = datetime.date.today()
        try:
            booking = await self.repository.create_booking(chat_id, date)
        except IntegrityError:
            booking = await self.repository.retrieve_booking(chat_id, date)
        return booking

    async def get_booking(self, chat_id: int, date: datetime.date | None = None) -> AfterDailyBookingDTO | None:
        if not date:
            date = datetime.date.today()
        return await self.repository.retrieve_booking(chat_id, date)

    async def get_all_bookings_for_date(self, date: datetime.date | None = None) -> list[AfterDailyBookingDTO]:
        if not date:
            date = datetime.date.today()
        return await self.repository.retrieve_all_bookings_for_day(date)

    async def update_booking(self, chat_id: int, date: datetime.date, win: bool) -> None:
        booking = await self.repository.retrieve_booking(chat_id, date)
        if not booking:
            return None
        await self.repository.update_booking(chat_id, date, win)

    async def remove_booking(self, chat_id: int, date: datetime.date | None = None) -> None:
        if not date:
            date = datetime.date.today()
        await self.repository.delete_booking(chat_id, date)
