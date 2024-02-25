import datetime

import pytz
from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from texts.start import WELCOME_TEXT
from handlers.after_daily import send_invitation
from keyboards import get_personal_game_kb
from middlewares import DBSessionMiddleware
from services.after_daily_booking_manager import AfterDailyBookingManager
from services.couple_tourney_manager import CoupleTourneyManager
from services.user_manager import UserManager
from utils.datetime import today_is_workday

router = Router(name='start')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id

    user_manager = UserManager(session)
    user_exists = await user_manager.get_user(chat_id)
    if not user_exists:
        await user_manager.add_user(chat_id)
    booking_exists = await AfterDailyBookingManager(session).get_booking(chat_id)
    now_in_tourney = await CoupleTourneyManager(session).get_active_tourney(chat_id)
    await message.bot.send_message(
        text=WELCOME_TEXT,
        chat_id=message.chat.id,
        reply_markup=get_personal_game_kb(now_in_tourney=True if now_in_tourney else False),
    )
    novosibirsk_dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Novosibirsk"))
    if not booking_exists and not today_is_workday() and novosibirsk_dt_now.time() < datetime.time(hour=14, minute=30):
        await send_invitation(message.bot, chat_id)
