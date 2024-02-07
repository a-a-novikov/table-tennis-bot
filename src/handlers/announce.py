from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from config import settings
from keyboards import get_personal_game_kb
from middlewares import DBSessionMiddleware
from services.user_manager import UserManager

router = Router(name='announce')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(lambda t: "announce" in t.text)
async def release_announce_handler(message: types.Message, session: AsyncSession):
    """
    Анонс релиза доступен админу. Для анонса нужно с админского профиля отправить сообщение
    вида:
    announce
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
        await message.bot.send_message(
            chat_id=u.chat_id,
            text=texts.PATCH_NOTE.format(version=version, content=content),
            reply_markup=get_personal_game_kb(),
            parse_mode=ParseMode.HTML,
        )
