from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from handlers.after_daily import send_invitation
from keyboards import get_personal_game_kb
from middlewares import DBSessionMiddleware
from services.after_daily_booking_manager import AfterDailyBookingManager
from services.couple_tourney_manager import CoupleTourneyManager
from services.user_manager import UserManager

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
        text=texts.WELCOME_TEXT,
        chat_id=message.chat.id,
        reply_markup=get_personal_game_kb(now_in_tourney=True if now_in_tourney else False),
    )
    if not booking_exists:
        await send_invitation(message.bot, chat_id)


@router.message(F.text == "Посмореть личную статистику")
async def init_tourney_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    user_stats = await UserManager(session).get_user_statistics(chat_id)
    if user_stats:
        await message.bot.send_message(
            chat_id=chat_id,
            text=texts.PERSONAL_STATISTICS.format(
                last_daily_game_date=user_stats.last_daily_game_date.isoformat() if user_stats.last_daily_game_date else "нет данных",
                daily_wins=user_stats.daily_wins,
                daily_total=user_stats.daily_total,
                couple_tourney_games_won=user_stats.couple_tourney_games_won,
                couple_tourney_games_total=user_stats.couple_tourney_games_total,
                couple_tourney_won=user_stats.couple_tourney_won,
                couple_tourney_total=user_stats.couple_tourney_total,
            ),
            parse_mode=ParseMode.HTML,
        )