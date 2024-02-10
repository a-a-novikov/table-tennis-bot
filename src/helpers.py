from datetime import date

from aiogram import types

from constants import EMOJI_BY_INT
from dto import EnrichedUserDTO


def get_pretty_name_from_chat(chat: types.Chat) -> str:
    if chat.first_name and chat.last_name:
        return f"{chat.first_name} «{chat.username}» {chat.last_name}"
    elif chat.first_name:
        return f"{chat.first_name} «{chat.username}»"
    elif chat.last_name:
        return f"«{chat.username}» {chat.last_name}"
    return f"«{chat.username}»"


def get_pretty_name_from_user_dto(user_dto: EnrichedUserDTO) -> str:
    if user_dto.first_name and user_dto.last_name:
        return f"{user_dto.first_name} «{user_dto.username}» {user_dto.last_name[0]}."
    elif user_dto.first_name:
        return f"{user_dto.first_name} «{user_dto.username}»"
    elif user_dto.last_name:
        return f"«{user_dto.username}» {user_dto.last_name}"
    return f"«{user_dto.username}»"


def parse_int_to_emoji_int(string_of_ints: int) -> str:
    result_str = ""
    for int_ in str(string_of_ints):
        result_str += EMOJI_BY_INT[int(int_)]
    return result_str


def check_if_today_is_holiday() -> bool:
    if date.today().weekday() > 4:
        return True
