import random
from datetime import date

from aiogram import F
from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from constants import MONTHS
from db.base import DBSessionFactory
from helpers import get_pretty_name_from_chat, check_if_today_is_holiday
from keyboards import registration_kb, RegistrationChoice, reset_registration_kb, game_result_kb, \
    GameResultChoice
from middlewares import DBSessionMiddleware
from services.after_daily_booking_manager import AfterDailyBookingManager
from services.user_manager import UserManager

router = Router(name='after_daily')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


async def send_invitation(bot, chat_id):
    today_date = f"{date.today().day} {MONTHS[date.today().month]}"
    await bot.send_message(
        chat_id=chat_id,
        text=texts.REGISTRATION_ANNOUNCE.format(date=today_date),
        reply_markup=registration_kb(),
    )


async def send_daily_invitation(bot):
    if check_if_today_is_holiday():
        return
    async with DBSessionFactory() as session:
        users = await UserManager(session).get_all_users()
    for user in users:
        try:
            await send_invitation(bot, user.chat_id)
        except TelegramBadRequest:
            print("bad request")


@router.callback_query(F.data == RegistrationChoice.IDLE.value)
async def registration_canceled_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    await AfterDailyBookingManager(session).remove_booking(chat_id)
    today_date = f"{date.today().day} {MONTHS[date.today().month]}"
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=texts.REGISTRATION_ANNOUNCE.format(date=today_date),
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
    confirmation_text = texts.REGISTRATION_CONFIRMED if request_status == RegistrationChoice.IN_GAME else texts.REGISTRATION_DECLINED
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=confirmation_text.format(date=today_date),
        reply_markup=reset_registration_kb(),
    )


async def send_paired_players_list(bot):
    if check_if_today_is_holiday():
        return
    async with DBSessionFactory() as session:
        bookings = await AfterDailyBookingManager(session).get_all_bookings_for_date()
    if not bookings:
        return

    # Удаляет из броней тех людей, которые заблокировали бота
    # TODO это костыль, нужен обработчик запросов с проверкой на доступность юзера
    for booking in bookings:
        try:
            await bot.get_chat(booking.user_id)
        except TelegramBadRequest:
            bookings.remove(booking)

    if len(bookings) == 1:
        try:
            await bot.send_message(
                chat_id=bookings[0].user_id,
                text=texts.TOO_LITTLE_BOOKINGS_FOR_AFTER_DAILY,
            )
        except TelegramBadRequest as e:
            print(e)
        finally:
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
    for pair_bookings in paired_bookings:
        try:
            p1_chat = await bot.get_chat(pair_bookings[0].user_id)
            p2_chat = await bot.get_chat(pair_bookings[1].user_id)
            paired_usernames.append([get_pretty_name_from_chat(p1_chat), get_pretty_name_from_chat(p2_chat)])
        except TelegramBadRequest as e:
            print(e)
    # При нечетном кол-ве броней, составляет слушчайную пару с оставшимся в соло игроком
    if unpaired:
        try:
            p1_chat = await bot.get_chat(unpaired.user_id)
            bookings.remove(unpaired)
            p2_chat = await bot.get_chat(random.choice(bookings).user_id)
            paired_usernames.append([get_pretty_name_from_chat(p1_chat), get_pretty_name_from_chat(p2_chat)])
        except TelegramBadRequest as e:
            print(e)

    # Отправляет список пар всем подписчикам бота
    for booking in bookings:
        try:
            await bot.send_message(
                chat_id=booking.user_id,
                text=texts.format_pairs_list(paired_usernames),
                parse_mode=ParseMode.HTML,
            )
        except TelegramBadRequest as e:
            print(e)


async def send_save_game_result_messages(bot):
    if check_if_today_is_holiday():
        return
    async with DBSessionFactory() as session:
        bookings = await AfterDailyBookingManager(session).get_all_bookings_for_date()
    for booking in bookings:
        await bot.send_message(
            chat_id=booking.user_id,
            text=texts.MARK_GAME_RESULT,
            reply_markup=game_result_kb(),
        )


@router.callback_query(lambda c: c.data == GameResultChoice.WIN.value)
@router.callback_query(lambda c: c.data == GameResultChoice.LOOSE.value)
@router.callback_query(lambda c: c.data == GameResultChoice.SKIPPED.value)
async def result_survey_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    game_result = GameResultChoice[callback.data]
    result_to_reply_text = {
        GameResultChoice.WIN: texts.WON_RESULT_MARKED,
        GameResultChoice.LOOSE: texts.LOOSE_RESULT_MARKED,
        GameResultChoice.SKIPPED: texts.SKIPPED_RESULT_MARKED,
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
