from enum import Enum

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, \
    InlineKeyboardButton, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from dto import EnrichedUserDTO, PokyBallDTO
from utils.text_formatters import get_pretty_name_from_user_dto


class RegistrationChoice(Enum):
    IN_GAME = "IN_GAME"
    PASS = "PASS"
    IDLE = "IDLE"


registration_cb_data = CallbackData()


class GameResultChoice(Enum):
    WIN = "WIN"
    LOOSE = "LOOSE"
    SKIPPED = "SKIPPED"


game_result_cb_data = CallbackData()


def registration_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Участвую 🏓", callback_data=RegistrationChoice.IN_GAME.value)
    builder.button(text="Работаю 👩🏻‍💻", callback_data=RegistrationChoice.PASS.value)
    return builder.as_markup()


def reset_registration_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сбросить регистрацию ↩️", callback_data=RegistrationChoice.IDLE.value)
    return builder.as_markup()


def game_result_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Gotcha 🏆", callback_data=GameResultChoice.WIN.value),
        InlineKeyboardButton(text="Габэлла 🐳", callback_data=GameResultChoice.LOOSE.value),

    )
    builder.row(
        InlineKeyboardButton(text="Пропустил игру", callback_data=GameResultChoice.SKIPPED.value)
    )
    return builder.as_markup()


def get_personal_game_kb(now_in_tourney: bool = False) -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Посмореть личную статистику")
    if now_in_tourney:
        builder.row(
            KeyboardButton(text="Инфа по текущей дуэли"),
            KeyboardButton(text="Записать дуэльную игру"),
        )
    else:
        builder.button(text="Организовать дуэль")
    builder.row(KeyboardButton(text="Установить титульный poky-ball"))
    return builder.as_markup(resize_keyboard=True)


def get_couple_tourney_cancel_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Отменить дуэль ⛔️", callback_data="cancel_tourney")
    return builder.as_markup()


async def get_users_available_for_tourney_kb(  # TODO remove session passing to the func
    users: list[EnrichedUserDTO],
    author_id: int,
    session: AsyncSession,
    offset: int = 0,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows = []
    users_amount = len(users)
    for idx in range(offset, users_amount, 2):
        if idx + 1 == users_amount:
            user = users[idx]
            user_name = await get_pretty_name_from_user_dto(user, session)
            rows.append(
                builder.row(
                    InlineKeyboardButton(
                        text=f"{user_name}",
                        callback_data=f"acceptor_{user.chat_id}_initiator_{author_id}",
                    ),
                )
            )
            continue
        user1, user2 = users[idx:idx + 2]
        user1_name = await get_pretty_name_from_user_dto(user1, session)
        user2_name = await get_pretty_name_from_user_dto(user2, session)
        new_row = builder.row(
            InlineKeyboardButton(
                text=f"{user1_name}",
                callback_data=f"acceptor_{user1.chat_id}_initiator_{author_id}",
            ),
            InlineKeyboardButton(
                text=f"{user2_name}",
                callback_data=f"acceptor_{user2.chat_id}_initiator_{author_id}",
            ),
        )
        rows.append(new_row)

    page_selector_buttons = []
    if offset == 0:
        next_page = InlineKeyboardButton(text="⏩️", callback_data=f"offset_10")
        page_selector_buttons.append(next_page)
    elif len(users) - offset <= 10:
        prev_page = InlineKeyboardButton(text="⏪️", callback_data=f"offset_{offset - 10}")
        page_selector_buttons.append(prev_page)
    else:
        prev_page = InlineKeyboardButton(text="⏪️", callback_data=f"offset_{offset - 10}")
        nex_page = InlineKeyboardButton(text="⏩️", callback_data=f"offset_{offset + 10}")
        page_selector_buttons.extend((prev_page, nex_page))
    rows.append(builder.row(*page_selector_buttons))

    return builder.as_markup()


def get_tourney_length_kb(acceptor_id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"До двух",
            callback_data=f"new-tourney_2_{acceptor_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"До трех",
            callback_data=f"new-tourney_3_{acceptor_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"До четырех",
            callback_data=f"new-tourney_4_{acceptor_id}",
        ),
    )
    return builder.as_markup()


async def get_tourney_game_result_kb(  # TODO remove session passing to the func
    initiator: EnrichedUserDTO,
    acceptor: EnrichedUserDTO,
    session: AsyncSession,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    initiator_name = await get_pretty_name_from_user_dto(initiator, session)
    acceptor_name = await get_pretty_name_from_user_dto(acceptor, session)
    builder.row(
        InlineKeyboardButton(
            text=f"Победил {initiator_name} 🟦", callback_data=f"game-winner_{initiator.chat_id}"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"Победил {acceptor_name} 🟥", callback_data=f"game-winner_{acceptor.chat_id}"
        ),
    )
    return builder.as_markup()


class TourneyAcceptanceChoice(Enum):
    IN_GAME = "IN_TOURNEY"
    PASS = "PASS_TOURNEY"


def get_tourney_acceptance_kb() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Вызов принят 🤝", callback_data=TourneyAcceptanceChoice.IN_GAME.value)
    builder.button(text="Imma out 🚪", callback_data=TourneyAcceptanceChoice.PASS.value)
    return builder.as_markup()


def get_choose_trophy_poky_ball_kb(
    owner_id: int,
    poky_balls: list[PokyBallDTO],
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ball in poky_balls:
        builder.button(text=ball.emoji, callback_data=f"trophy-poky_{ball.id}_{owner_id}")
    return builder.as_markup()


def get_setup_title_poky_ball_kb(
    poky_balls: list[PokyBallDTO],
    title_poky_ball_id: int | None,
) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ball in poky_balls:
        text = f"{ball.emoji} (титульный)" if ball.id == title_poky_ball_id else ball.emoji
        builder.button(text=text, callback_data=f"title-poky_{ball.id}")
    builder.adjust(2)
    return builder.as_markup()
