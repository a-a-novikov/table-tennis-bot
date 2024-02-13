from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

import texts
from helpers import get_pretty_name_from_chat, get_pretty_name_from_user_dto, parse_int_to_emoji_int
from keyboards import get_users_available_for_tourney_kb, get_tourney_length_kb, \
    get_personal_game_kb, get_tourney_game_result_kb, get_tourney_acceptance_kb, \
    TourneyAcceptanceChoice, get_couple_tourney_cancel_kb
from middlewares import DBSessionMiddleware
from services.couple_tourney_manager import CoupleTourneyManager
from services.user_manager import UserManager

router = Router(name='couple_tourney')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(F.text == "Организовать дуэль")
async def init_tourney_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    users = await UserManager(session).get_all_users_enriched(message.bot)
    users_available_for_tourney = await CoupleTourneyManager(session).get_users_available_for_tourney(users, chat_id)
    await message.answer(
        text=texts.ACCEPTOR_SELECTION,
        reply_markup=get_users_available_for_tourney_kb(users_available_for_tourney, chat_id),
    )


@router.message(F.text == "Инфа по текущей дуэли")
async def init_tourney_handler(message: types.Message, session: AsyncSession):
    tourney = await CoupleTourneyManager(session).get_active_tourney(message.chat.id)

    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(tourney.initiator_id, message.bot)
    acceptor = await user_manager.get_user_enriched(tourney.acceptor_id, message.bot)
    await message.answer(
        text=texts.get_current_tourney_info(
            wins_total=tourney.wins_total,
            day=tourney.registered_at.day,
            month=tourney.registered_at.month,
            initiator_name=get_pretty_name_from_user_dto(initiator),
            initiator_wins=tourney.initiator_wins,
            acceptor_name=get_pretty_name_from_user_dto(acceptor),
            acceptor_wins=tourney.acceptor_wins,
        ),
        reply_markup=get_couple_tourney_cancel_kb(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(lambda c: c.data == "cancel_tourney")
async def cancel_active_tourney_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    tourney_manager = CoupleTourneyManager(session)

    current_tourney = await tourney_manager.get_active_tourney(chat_id)
    if not current_tourney:
        return None
    await tourney_manager.finish_tourney(chat_id)

    await callback.message.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    await callback.message.answer(
        text=texts.TOURNEY_MANUALLY_FINISHED,
        reply_markup=get_personal_game_kb(),
    )
    await callback.bot.send_message(
        chat_id=current_tourney.acceptor_id if current_tourney.initiator_id == chat_id else current_tourney.acceptor_id,
        text=texts.TOURNEY_MANUALLY_FINISHED,
        reply_markup=get_personal_game_kb(),
    )


@router.message(F.text == "Записать дуэльную игру")
async def init_tourney_handler(message: types.Message, session: AsyncSession):
    tourney = await CoupleTourneyManager(session).get_active_tourney(message.chat.id)

    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(tourney.initiator_id, message.bot)
    acceptor = await user_manager.get_user_enriched(tourney.acceptor_id, message.bot)
    await message.answer(
        text=texts.TOURNEY_GAME_RESULT_SELECTION,
        reply_markup=get_tourney_game_result_kb(initiator, acceptor),
    )


@router.callback_query(lambda c: c.data == TourneyAcceptanceChoice.IN_GAME.value)
@router.callback_query(lambda c: c.data == TourneyAcceptanceChoice.PASS.value)
async def accept_or_decline_tourney_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    tourney_manager = CoupleTourneyManager(session)
    tourney = await tourney_manager.get_active_tourney(chat_id)
    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(tourney.initiator_id, callback.bot)
    acceptor = await user_manager.get_user_enriched(tourney.acceptor_id, callback.bot)
    is_tourney_accepted = callback.data == TourneyAcceptanceChoice.IN_GAME.value
    if is_tourney_accepted:
        await tourney_manager.accept_tourney(chat_id)
        text = texts.TOURNEY_ACCEPTED
    else:
        await tourney_manager.decline_tourney(chat_id)
        text = texts.TOURNEY_DECLINED.format(
            initiator=get_pretty_name_from_user_dto(initiator),
            acceptor=get_pretty_name_from_user_dto(acceptor),
        )

    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    for user_id in (tourney.initiator_id, tourney.acceptor_id):
        await callback.bot.send_message(
            chat_id=user_id,
            text=text.format(
                initiator=get_pretty_name_from_user_dto(initiator),
                acceptor=get_pretty_name_from_user_dto(acceptor),
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_personal_game_kb(now_in_tourney=True if is_tourney_accepted else False)
        )


@router.callback_query(lambda c: "game-winner_" in c.data)
async def process_tourney_game_result_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    winner_id = int(callback.data.replace("game-winner_", ""))
    tourney_manager = CoupleTourneyManager(session)
    tourney = await tourney_manager.update_active_tourney_score(winner_id)
    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )

    user_manager = UserManager(session)
    if tourney.initiator_wins == tourney.wins_total:
        winner_id, looser_id = tourney.initiator_id, tourney.acceptor_id
        winner_wins = tourney.initiator_wins
        looser_wins = tourney.acceptor_wins
        await tourney_manager.finish_tourney(winner_id)
    elif tourney.acceptor_wins == tourney.wins_total:
        winner_id, looser_id = tourney.acceptor_id, tourney.initiator_id
        winner_wins = tourney.acceptor_wins
        looser_wins = tourney.initiator_wins
        await tourney_manager.finish_tourney(winner_id)
    else:
        winner_id = tourney.initiator_id if tourney.initiator_id == winner_id else tourney.acceptor_id
        looser_id = tourney.acceptor_id if tourney.initiator_id == winner_id else tourney.initiator_id
        winner_wins = tourney.initiator_wins if tourney.initiator_id == winner_id else tourney.acceptor_wins
        looser_wins = tourney.acceptor_wins if tourney.initiator_id == winner_id else tourney.initiator_wins
    winner = await user_manager.get_user_enriched(winner_id, callback.bot)
    looser = await user_manager.get_user_enriched(looser_id, callback.bot)

    for user_id in (tourney.initiator_id, tourney.acceptor_id):
        winner_pretty_name = get_pretty_name_from_user_dto(winner)
        looser_pretty_name = get_pretty_name_from_user_dto(looser)
        # дуэль завершена
        if tourney.wins_total in (tourney.initiator_wins, tourney.acceptor_wins):
            await callback.bot.send_message(
                chat_id=user_id,
                text=texts.TOURNEY_FINISHED.format(
                    winner=winner_pretty_name,
                    winner_wins=tourney.wins_total,
                    loser=looser_pretty_name,
                    looser_wins=looser_wins,
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=get_personal_game_kb(),
            )
        # дуэль еще продолжается
        else:
            await callback.bot.send_message(
                chat_id=user_id,
                text=texts.TOURNEY_GAME_RESULT_RECORDED.format(
                    player1_wins=parse_int_to_emoji_int(winner_wins),
                    player1=winner_pretty_name,
                    player2_wins=parse_int_to_emoji_int(looser_wins),
                    player2=looser_pretty_name,
                ),
                parse_mode=ParseMode.HTML,
            )


@router.callback_query(lambda c: "offset_" in c.data)
async def change_users_page_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    offset = int(callback.data.replace("offset_", ""))
    users = await UserManager(session).get_all_users_enriched(callback.message.bot)
    users_available_for_tourney = await CoupleTourneyManager(session).get_users_available_for_tourney(users, chat_id)

    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=texts.ACCEPTOR_SELECTION,
        reply_markup=get_users_available_for_tourney_kb(users_available_for_tourney, chat_id, offset),
    )


@router.callback_query(lambda c: "acceptor_" in c.data)
async def process_acceptor_choice_handler(callback: types.CallbackQuery, session: AsyncSession):
    acceptor_id = int(callback.data.split("_")[1])
    initiator_id = int(callback.data.split("_")[3])
    active_tourney = await CoupleTourneyManager(session).get_active_tourney(initiator_id)
    if active_tourney:
        await callback.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
        )
    acceptor_chat = await callback.message.bot.get_chat(acceptor_id)
    acceptor_name = get_pretty_name_from_chat(acceptor_chat)
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=texts.ACCEPTOR_SELECTED.format(acceptor=acceptor_name),
        reply_markup=get_tourney_length_kb(acceptor_id),
    )


@router.callback_query(lambda c: "new-tourney_" in c.data)
async def process_tourney_length_choice_handler(callback: types.CallbackQuery, session: AsyncSession):
    initiator_id = callback.message.chat.id
    tourney_info = callback.data.replace("new-tourney_", "")
    wins_total, acceptor_id = map(int, tourney_info.split("_"))
    tourney_manager = CoupleTourneyManager(session)
    active_tourney = await CoupleTourneyManager(session).get_active_tourney(initiator_id)
    if active_tourney:
        await callback.bot.delete_message(
            chat_id=initiator_id,
            message_id=callback.message.message_id,
        )
    initiator = await UserManager(session).get_user_enriched(initiator_id, callback.bot)
    await tourney_manager.add_tourney(
        initiator_id=initiator_id,
        acceptor_id=acceptor_id,
        wins_total=wins_total,
    )
    await callback.message.bot.delete_message(
        chat_id=initiator_id,
        message_id=callback.message.message_id,
    )
    await callback.message.answer(
        text=texts.TOURNEY_REGISTERED,
        reply_markup=get_personal_game_kb(now_in_tourney=True),
    )
    await callback.bot.send_message(
        chat_id=acceptor_id,
        text=texts.ACCEPTION_REQUEST.format(initiator=get_pretty_name_from_user_dto(initiator)),
        reply_markup=get_tourney_acceptance_kb(),
    )