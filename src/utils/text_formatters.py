from sqlalchemy.ext.asyncio import AsyncSession

from constants import EMOJI_BY_INT
from dto import EnrichedUserDTO
from services.poky_ball_manager import PokyBallManager


async def get_pretty_name_from_user_dto(user_dto: EnrichedUserDTO, session: AsyncSession) -> str:  # TODO remove passing of session to the func
    title_poky = ""
    if user_dto.title_poky_id:
        poky_ball = await PokyBallManager(session).get_poky_ball(user_dto.title_poky_id)
        title_poky = f"{poky_ball.emoji} "

    if user_dto.first_name and user_dto.last_name:
        return f"{title_poky}{user_dto.first_name} «{user_dto.username}» {user_dto.last_name[0]}."
    elif user_dto.first_name:
        return f"{title_poky}{user_dto.first_name} «{user_dto.username}»"
    elif user_dto.last_name:
        return f"«{title_poky}{user_dto.username}» {user_dto.last_name}"
    return f"«{title_poky}{user_dto.username}»"


def parse_int_to_emoji_int(string_of_ints: int) -> str:
    result_str = ""
    for int_ in str(string_of_ints):
        result_str += EMOJI_BY_INT[int(int_)]
    return result_str
