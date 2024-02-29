from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import get_setup_title_poky_ball_kb
from services.poky_ball_manager import PokyBallManager
from texts.personal_stats import PERSONAL_STATISTICS, TITLE_POKY_SET, NO_POKIES_TO_SET_AS_TITLE, \
    CHOOSE_TITLE_POKY
from utils.text_formatters import parse_int_to_emoji_int
from middlewares import DBSessionMiddleware
from services.user_manager import UserManager

router = Router(name='personal_stats')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(F.text == "Посмореть личную статистику")
async def personal_stats_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    user_manager = UserManager(session)
    user = await user_manager.get_user(chat_id)
    user_stats = await user_manager.get_user_statistics(chat_id)
    poky_manager = PokyBallManager(session)
    poky_balls = await poky_manager.get_all_poky_balls_by_owner(chat_id)

    poky_balls_text = " | ".join((b.emoji for b in poky_balls)) if poky_balls else "их нет :("
    if user.title_poky_id:
        title_poky = await poky_manager.get_poky_ball(user.title_poky_id)
        poky_balls_text = poky_balls_text.replace(title_poky.emoji, f"({title_poky.emoji})")

    if user_stats:
        await message.bot.send_message(
            chat_id=chat_id,
            text=PERSONAL_STATISTICS.format(
                poky_balls=poky_balls_text,
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


@router.message(F.text == "Установить титульный poky-ball")
async def personal_stats_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    user_manager = UserManager(session)
    user = await user_manager.get_user(chat_id)
    poky_manager = PokyBallManager(session)
    poky_balls = await poky_manager.get_all_poky_balls_by_owner(chat_id)
    if not poky_balls:
        await message.bot.send_message(chat_id=chat_id, text=NO_POKIES_TO_SET_AS_TITLE)
        return None

    await message.bot.send_message(
        chat_id=chat_id,
        text=CHOOSE_TITLE_POKY,
        reply_markup=get_setup_title_poky_ball_kb(poky_balls, user.title_poky_id),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(lambda c: "title-poky_" in c.data)
async def title_poky_ball_chosen_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    poky_ball_id = int(callback.data.replace("title-poky_", ""))
    poky_ball_manager = PokyBallManager(session)
    poky_ball = await poky_ball_manager.get_poky_ball(poky_ball_id)

    if poky_ball.owner_id != chat_id:
        return None

    user_manager = UserManager(session)
    user = await user_manager.get_user(chat_id)
    user.title_poky_id = poky_ball.id
    await user_manager.update_user(user)

    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=TITLE_POKY_SET.format(emoji=poky_ball.emoji),
    )
