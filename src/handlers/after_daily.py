import logging
import random
from datetime import date

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from texts.after_daily import REGISTRATION_ANNOUNCE, REGISTRATION_CONFIRMED, REGISTRATION_DECLINED, \
    TOO_LITTLE_BOOKINGS_FOR_AFTER_DAILY, format_pairs_list, MARK_GAME_RESULT, WON_RESULT_MARKED, \
    LOOSE_RESULT_MARKED, SKIPPED_RESULT_MARKED
from constants import MONTHS
from db.base import DBSessionFactory
from utils.text_formatters import get_pretty_name_from_user_dto
from keyboards import registration_kb, RegistrationChoice, reset_registration_kb, game_result_kb, \
    GameResultChoice
from middlewares import DBSessionMiddleware
from services.after_daily_booking_manager import AfterDailyBookingManager
from services.user_manager import UserManager

router = Router(name='after_daily')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


async def send_invitation(bot, chat_id, session):
    today_date = f"{date.today().day} {MONTHS[date.today().month]}"
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=REGISTRATION_ANNOUNCE.format(date=today_date),
            reply_markup=registration_kb(),
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        await UserManager(session).mark_user_as_deleted(chat_id)
        logging.warning(f"Failed send daily invite to chat_id={chat_id}")


async def send_daily_invitation(bot):
    async with DBSessionFactory() as session:
        users = await UserManager(session).get_all_users()
        for user in users:
            await send_invitation(bot, user.chat_id, session)


@router.callback_query(F.data == RegistrationChoice.IDLE.value)
async def registration_canceled_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    await AfterDailyBookingManager(session).remove_booking(chat_id)
    today_date = f"{date.today().day} {MONTHS[date.today().month]}"
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=REGISTRATION_ANNOUNCE.format(date=today_date),
        reply_markup=registration_kb(),
    )


@router.callback_query(lambda c: c.data == RegistrationChoice.IN_GAME.value)
@router.callback_query(lambda c: c.data == RegistrationChoice.PASS.value)
async def registration_survey_handler(callback: types.CallbackQuery, session: AsyncSession):
    after_daily_booking_manager = AfterDailyBookingManager(session)
    request_status = RegistrationChoice[callback.data]
    chat_id = callback.message.chat.id

    is_registered = await after_daily_booking_manager.get_booking(chat_id)
    if not is_registered and request_status == RegistrationChoice.IN_GAME:
        await after_daily_booking_manager.add_booking(chat_id)
    today_date = f"{date.today().day} {MONTHS[date.today().month]}"
    confirmation_text = REGISTRATION_CONFIRMED if request_status == RegistrationChoice.IN_GAME else REGISTRATION_DECLINED
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=confirmation_text.format(date=today_date),
        reply_markup=reset_registration_kb(),
    )


async def send_paired_players_list(bot):
    async with DBSessionFactory() as session:
        bookings = await AfterDailyBookingManager(session).get_all_bookings_for_date()
    if not bookings:
        return

    # Удаляет из броней тех людей, которые заблокировали бота
    # TODO это костыль, нужен обработчик запросов с проверкой на доступность юзера
    for booking in bookings:
        try:
            await bot.get_chat(booking.user_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            logging.warning(f"User with chat_id={booking.user_id} is unavailable")
            await UserManager(session).mark_user_as_deleted(booking.user_id)
            bookings.remove(booking)

    if len(bookings) == 1:
        await bot.send_message(
            chat_id=bookings[0].user_id,
            text=TOO_LITTLE_BOOKINGS_FOR_AFTER_DAILY,
        )
        return None

    bookings_set = set(bookings)
    paired_bookings = []
    unpaired = None
    # Формирует пары ID игроков случайным образом
    while bookings_set:
        try:
            pair = random.sample(sorted(bookings_set), 2)
            paired_bookings.append(pair)
        except ValueError:
            unpaired = bookings_set.pop()
            break
        else:
            bookings_set -= set(pair)

    # Получает имена для распределенных по парам подписчиков
    paired_usernames = []
    user_manager = UserManager(session)
    for pair_bookings in paired_bookings:
        p1 = await user_manager.get_user_enriched(pair_bookings[0].user_id, bot)
        p2 = await user_manager.get_user_enriched(pair_bookings[1].user_id, bot)
        p1_name = await get_pretty_name_from_user_dto(p1, session)
        p2_name = await get_pretty_name_from_user_dto(p2, session)
        paired_usernames.append([p1_name, p2_name])
    # При нечетном кол-ве броней, составляет слушчайную пару с оставшимся в соло игроком
    if unpaired:
        p1 = await user_manager.get_user_enriched(unpaired.user_id, bot)
        bookings.remove(unpaired)
        p2 = await user_manager.get_user_enriched(random.choice(bookings).user_id, bot)
        p1_name = await get_pretty_name_from_user_dto(p1, session)
        p2_name = await get_pretty_name_from_user_dto(p2, session)
        paired_usernames.append([p1_name, p2_name])

    # Отправляет список пар всем подписчикам бота
    for booking in bookings:
        await bot.send_message(
            chat_id=booking.user_id,
            text=format_pairs_list(paired_usernames),
            parse_mode=ParseMode.HTML,
        )


async def send_save_game_result_messages(bot):
    async with DBSessionFactory() as session:
        bookings = await AfterDailyBookingManager(session).get_all_bookings_for_date()
    for booking in bookings:
        await bot.send_message(
            chat_id=booking.user_id,
            text=MARK_GAME_RESULT,
            reply_markup=game_result_kb(),
        )


@router.callback_query(lambda c: c.data == GameResultChoice.WIN.value)
@router.callback_query(lambda c: c.data == GameResultChoice.LOOSE.value)
@router.callback_query(lambda c: c.data == GameResultChoice.SKIPPED.value)
async def result_survey_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    game_result = GameResultChoice[callback.data]
    result_to_reply_text = {
        GameResultChoice.WIN: WON_RESULT_MARKED,
        GameResultChoice.LOOSE: LOOSE_RESULT_MARKED,
        GameResultChoice.SKIPPED: SKIPPED_RESULT_MARKED,
    }
    if game_result in (GameResultChoice.WIN, game_result.LOOSE):
        await AfterDailyBookingManager(session).update_booking(
            chat_id=chat_id,
            date=date.today(),
            win=game_result == GameResultChoice.WIN,
        )
    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    await callback.bot.send_message(
        chat_id=chat_id,
        text=result_to_reply_text[game_result],
    )
