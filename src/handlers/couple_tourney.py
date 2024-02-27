from aiogram import Router, types, F
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from services.poky_ball_manager import PokyBallManager
from texts.couple_tourney import ACCEPTOR_SELECTION, get_current_tourney_info, \
    TOURNEY_MANUALLY_FINISHED, TOURNEY_GAME_RESULT_SELECTION, TOURNEY_ACCEPTED, TOURNEY_DECLINED, \
    TOURNEY_FINISHED, TOURNEY_GAME_RESULT_RECORDED, ACCEPTOR_SELECTED, TOURNEY_REGISTERED, \
    ACCEPTION_REQUEST, CHOOSE_TROPHY_POKY_BALL, TROPHY_POKY_BALL_RETRIEVED, POKY_BALL_LOST
from utils.text_formatters import get_pretty_name_from_user_dto, \
    parse_int_to_emoji_int
from keyboards import get_users_available_for_tourney_kb, get_tourney_length_kb, \
    get_personal_game_kb, get_tourney_game_result_kb, get_tourney_acceptance_kb, \
    TourneyAcceptanceChoice, get_couple_tourney_cancel_kb, get_choose_trophy_poky_ball_kb
from middlewares import DBSessionMiddleware
from services.couple_tourney_manager import CoupleTourneyManager
from services.user_manager import UserManager

router = Router(name='couple_tourney')

router.message.middleware(DBSessionMiddleware())
router.callback_query.middleware(DBSessionMiddleware())


@router.message(F.text == "Организовать дуэль")
async def new_tourney_request_handler(message: types.Message, session: AsyncSession):
    chat_id = message.chat.id
    users = await UserManager(session).get_all_users_enriched(message.bot)
    users_available_for_tourney = await CoupleTourneyManager(session).get_users_available_for_tourney(users, chat_id)
    reply_markup = await get_users_available_for_tourney_kb(users_available_for_tourney, chat_id, session)
    await message.answer(
        text=ACCEPTOR_SELECTION,
        reply_markup=reply_markup,
    )


@router.message(F.text == "Инфа по текущей дуэли")
async def tourney_info_handler(message: types.Message, session: AsyncSession):
    tourney = await CoupleTourneyManager(session).get_active_tourney(message.chat.id)

    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(tourney.initiator_id, message.bot)
    acceptor = await user_manager.get_user_enriched(tourney.acceptor_id, message.bot)
    initiator_name = await get_pretty_name_from_user_dto(initiator, session)
    acceptor_name = await get_pretty_name_from_user_dto(acceptor, session)
    await message.answer(
        text=get_current_tourney_info(
            wins_total=tourney.wins_total,
            day=tourney.registered_at.day,
            month=tourney.registered_at.month,
            initiator_name=initiator_name,
            initiator_wins=tourney.initiator_wins,
            acceptor_name=acceptor_name,
            acceptor_wins=tourney.acceptor_wins,
        ),
        reply_markup=get_couple_tourney_cancel_kb(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(lambda c: c.data == "cancel_tourney")
async def cancel_tourney_request_handler(callback: types.CallbackQuery, session: AsyncSession):
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

    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(chat_id, callback.bot)  # TODO refactor getting name of user - go DRY
    initiator_name = await get_pretty_name_from_user_dto(initiator, session)
    acceptor_id = current_tourney.acceptor_id if current_tourney.initiator_id == chat_id else current_tourney.acceptor_id
    acceptor = await user_manager.get_user_enriched(acceptor_id, callback.bot)
    acceptor_name = await get_pretty_name_from_user_dto(acceptor, session)

    await callback.message.answer(
        text=TOURNEY_MANUALLY_FINISHED.format(initiator=initiator_name, acceptor=acceptor_name),
        parse_mode=ParseMode.HTML,
        reply_markup=get_personal_game_kb(),
    )
    await callback.bot.send_message(
        chat_id=acceptor_id,
        text=TOURNEY_MANUALLY_FINISHED.format(initiator=initiator_name, acceptor=acceptor_name),
        parse_mode=ParseMode.HTML,
        reply_markup=get_personal_game_kb(),
    )


@router.message(F.text == "Записать дуэльную игру")
async def new_game_to_record_handler(message: types.Message, session: AsyncSession):
    tourney = await CoupleTourneyManager(session).get_active_tourney(message.chat.id)

    user_manager = UserManager(session)
    initiator = await user_manager.get_user_enriched(tourney.initiator_id, message.bot)
    acceptor = await user_manager.get_user_enriched(tourney.acceptor_id, message.bot)
    reply_markup = await get_tourney_game_result_kb(initiator, acceptor, session)
    await message.answer(
        text=TOURNEY_GAME_RESULT_SELECTION,
        reply_markup=reply_markup,
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
    initiator_name = await get_pretty_name_from_user_dto(initiator, session)  # TODO refactor of func - cross-layer dependency
    acceptor_name = await get_pretty_name_from_user_dto(acceptor, session)
    is_tourney_accepted = callback.data == TourneyAcceptanceChoice.IN_GAME.value
    if is_tourney_accepted:
        await tourney_manager.accept_tourney(chat_id)
        text = TOURNEY_ACCEPTED
    else:
        await tourney_manager.decline_tourney(chat_id)
        text = TOURNEY_DECLINED.format(
            initiator=initiator_name,
            acceptor=acceptor_name,
        )

    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    for user_id in (tourney.initiator_id, tourney.acceptor_id):
        await callback.bot.send_message(
            chat_id=user_id,
            text=text.format(
                initiator=initiator_name,
                acceptor=acceptor_name,
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

    if winner_id == tourney.initiator_id:
        winner_id, winner_wins = tourney.initiator_id, tourney.initiator_wins
        looser_id, looser_wins = tourney.acceptor_id, tourney.acceptor_wins
    else:
        winner_id, winner_wins = tourney.acceptor_id, tourney.acceptor_wins
        looser_id, looser_wins = tourney.initiator_id, tourney.initiator_wins

    user_manager = UserManager(session)
    winner = await user_manager.get_user_enriched(winner_id, callback.bot)
    looser = await user_manager.get_user_enriched(looser_id, callback.bot)
    winner_pretty_name = await get_pretty_name_from_user_dto(winner, session)
    looser_pretty_name = await get_pretty_name_from_user_dto(looser, session)

    for user_id in (tourney.initiator_id, tourney.acceptor_id):
        if tourney.is_finished:
            await callback.bot.send_message(
                chat_id=user_id,
                text=TOURNEY_FINISHED.format(
                    winner=winner_pretty_name,
                    winner_wins=tourney.wins_total,
                    loser=looser_pretty_name,
                    looser_wins=looser_wins,
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=get_personal_game_kb(),
            )
        else:
            await callback.bot.send_message(
                chat_id=user_id,
                text=TOURNEY_GAME_RESULT_RECORDED.format(
                    player1_wins=parse_int_to_emoji_int(winner_wins),
                    player1=winner_pretty_name,
                    player2_wins=parse_int_to_emoji_int(looser_wins),
                    player2=looser_pretty_name,
                ),
                parse_mode=ParseMode.HTML,
            )

    if tourney.is_finished:
        looser_poky_balls = await PokyBallManager(session).get_all_poky_balls_by_owner(looser_id)
        if looser_poky_balls:
            await callback.bot.send_message(
                chat_id=winner_id,
                text=CHOOSE_TROPHY_POKY_BALL,
                parse_mode=ParseMode.HTML,
                reply_markup=get_choose_trophy_poky_ball_kb(looser_id, looser_poky_balls),
            )


@router.callback_query(lambda c: "trophy-poky_" in c.data)
async def trophy_poky_ball_chosen_handler(callback: types.CallbackQuery, session: AsyncSession):
    chat_id = callback.message.chat.id
    await callback.bot.delete_message(
        chat_id=chat_id,
        message_id=callback.message.message_id,
    )
    poky_ball_id, trophy_owner_id = map(int, callback.data.replace("trophy-poky_", "").split("_"))
    poky_ball_manager = PokyBallManager(session)
    poky_ball = await poky_ball_manager.get_poky_ball(poky_ball_id)
    if poky_ball.owner_id != trophy_owner_id:
        return None

    updated_poky_ball = await poky_ball_manager.update_poky_ball_owner(chat_id, poky_ball_id)
    user_manager = UserManager(session)
    prev_poky_owner = await user_manager.get_user(trophy_owner_id)
    if prev_poky_owner.title_poky_id == poky_ball_id:
        prev_poky_owner.title_poky_id = None
        await user_manager.update_user(prev_poky_owner)

    await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=TROPHY_POKY_BALL_RETRIEVED.format(emoji=updated_poky_ball.emoji),
    )
    await callback.bot.send_message(
        chat_id=trophy_owner_id,
        text=POKY_BALL_LOST.format(emoji=updated_poky_ball.emoji),
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
        text=ACCEPTOR_SELECTION,
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

    acceptor = await UserManager(session).get_user_enriched(acceptor_id, callback.bot)
    acceptor_name = await get_pretty_name_from_user_dto(acceptor, session)

    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=ACCEPTOR_SELECTED.format(acceptor=acceptor_name),
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
        text=TOURNEY_REGISTERED,
        reply_markup=get_personal_game_kb(now_in_tourney=True),
    )
    initiator_name = await get_pretty_name_from_user_dto(initiator, session)
    await callback.bot.send_message(
        chat_id=acceptor_id,
        text=ACCEPTION_REQUEST.format(initiator=initiator_name),
        reply_markup=get_tourney_acceptance_kb(),
    )
