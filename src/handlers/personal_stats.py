from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from helpers import parse_int_to_emoji_int
from middlewares import DBSessionMiddleware
from services.user_manager import UserManager

router = Router(name='personal_stats')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(F.text == "Посмореть личную статистику")
async def personal_stats_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    user_stats = await UserManager(session).get_user_statistics(chat_id)
    if user_stats:
        await message.bot.send_message(
            chat_id=chat_id,
            text=texts.PERSONAL_STATISTICS.format(
                last_daily_game_date=user_stats.last_daily_game_date.isoformat() if user_stats.last_daily_game_date else "нет данных",
                daily_wins=parse_int_to_emoji_int(user_stats.daily_wins),
                daily_total=parse_int_to_emoji_int(user_stats.daily_total),
                couple_tourney_games_won=parse_int_to_emoji_int(user_stats.couple_tourney_games_won),
                couple_tourney_games_total=parse_int_to_emoji_int(user_stats.couple_tourney_games_total),
                couple_tourney_won=parse_int_to_emoji_int(user_stats.couple_tourney_won),
                couple_tourney_total=parse_int_to_emoji_int(user_stats.couple_tourney_total),
            ),
            parse_mode=ParseMode.HTML,
        )
