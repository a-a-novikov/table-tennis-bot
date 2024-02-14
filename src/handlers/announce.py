from aiogram import Router, types
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from config import settings
from keyboards import get_personal_game_kb
from middlewares import DBSessionMiddleware
from services.couple_tourney_manager import CoupleTourneyManager
from services.user_manager import UserManager

router = Router(name='announce')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(lambda t: "--release--" in t.text)
async def release_handler(message: types.Message, session: AsyncSession):
    """
    Анонс релиза доступен админу. Для анонса нужно с админского профиля отправить сообщение
    вида:
    --release--
    1.2.3
    - New feature A
    - <b>NEW EXTRA COOL FEATURE B</b>
    """
    if message.chat.id not in settings.ADMIN_CHAT_IDS:
        return None

    _, version, *content_as_list = message.text.split("\n")
    content = '\n'.join(content_as_list)

    users = await UserManager(session).get_all_users()
    for u in users:
        now_in_tourney = await CoupleTourneyManager(session).get_active_tourney(u.chat_id)
        await message.bot.send_message(
            chat_id=u.chat_id,
            text=texts.PATCH_NOTE.format(version=version, content=content),
            reply_markup=get_personal_game_kb(now_in_tourney=True if now_in_tourney else False),
            parse_mode=ParseMode.HTML,
        )


@router.message(lambda t: "--announce--" in t.text)
async def announce_handler(message: types.Message, session: AsyncSession):
    """
    Анонс информации доступен админу. Для анонса нужно с админского профиля отправить сообщение
    вида:
    --announce--
    Третьего дня купил себе фикус. Держу в курсе!
    """
    if message.chat.id not in settings.ADMIN_CHAT_IDS:
        return None

    _, *content_as_list = message.text.split("\n")
    content = '\n'.join(content_as_list)

    users = await UserManager(session).get_all_users()
    for u in users:
        now_in_tourney = await CoupleTourneyManager(session).get_active_tourney(u.chat_id)
        await message.bot.send_message(
            chat_id=u.chat_id,
            text=texts.ANNOUNCE.format(content=content),
            reply_markup=get_personal_game_kb(now_in_tourney=True if now_in_tourney else False),
            parse_mode=ParseMode.HTML,
        )
