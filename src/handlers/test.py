from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import get_personal_game_kb
from middlewares import DBSessionMiddleware
from services.user_manager import UserManager

router = Router(name='test')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(F.text == "db")
async def db_handler(message: types.Message, session: AsyncSession):
    # await UserManager().add_user(message.chat.id)
    # await UserManager().update_user_daily_streak(message.chat.id, True)
    # result = await UserManager().save_game_result(message.chat.id, True)
    # result = await UserManager(session).get_all_users()
    # x = []
    # for u in result:
    #     try:
    #
    #     except:
    #         pass
    await message.bot.send_message(
        chat_id=358830184,
        text="Доступно новое",
        reply_markup=get_personal_game_kb()
    )


@router.message(F.text == "announce")
async def announce_handler(message: types.Message, session: AsyncSession):
    # users = await UserManager(session).get_all_users()
    users = await UserManager(session).get_user(358830184)
    users = [users]
    TEXT = ("Обновление бота v0.2.1🔥\n"
            "\n"
            "<b>Изменения:</b>\n"
            "- Добавлена личная статистика (ищи кнопку под клавиатурой ⬇️)\n"
            "- Турниры 1 на 1 переименованы в дуэли\n"
            "- Добавлена возможность отмены активной дуэли\n"
            "- Исправлены ошибки регистрации турнира")
    for u in users:
        await message.bot.send_message(
            chat_id=u.chat_id,
            text=TEXT,
            reply_markup=get_personal_game_kb(),
            parse_mode=ParseMode.HTML,
        )
