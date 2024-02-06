import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from dto import UserDTO, EnrichedUserDTO, UserStatisticsDTO
from repositories.user import UserRepository


class UserManager:
    def __init__(self, session: AsyncSession):
        self.repository: UserRepository = UserRepository(session)

    async def add_user(self, chat_id: int) -> UserDTO:
        try:
            user = await self.repository.create_user(UserDTO(chat_id=chat_id))
        except IntegrityError:
            user = await self.repository.retrieve_user(chat_id)
        return UserDTO.from_db(user)

    async def get_user(self, chat_id: int) -> UserDTO | None:
        user = await self.repository.retrieve_user(chat_id)
        if not user:
            return None
        return UserDTO.from_db(user)

    async def get_user_enriched(self, chat_id: int, bot: Bot) -> EnrichedUserDTO | None:
        user = await self.repository.retrieve_user(chat_id)
        try:
            user_chat = await bot.get_chat(chat_id=user.chat_id)
        except TelegramBadRequest:
            return None
        return EnrichedUserDTO(
            chat_id=user.chat_id,
            username=user_chat.username,
            first_name=user_chat.first_name,
            last_name=user_chat.last_name,
            longest_streak=user.longest_streak,
            last_game_at=user.last_game_at,
            skip_count=user.skip_count,
            wins=user.wins,
            looses=user.looses,
        )

    async def get_all_users(self) -> list[UserDTO]:
        users = await self.repository.retrieve_all_users()
        return [
            UserDTO(
                chat_id=u.chat_id,
                longest_streak=u.longest_streak,
                last_game_at=u.last_game_at,
                skip_count=u.skip_count,
                wins=u.wins,
                looses=u.looses,
        )
            for u in users
        ]
    
    async def get_all_users_enriched(self, bot: Bot) -> list[EnrichedUserDTO]:
        users = await self.repository.retrieve_all_users()
        result = []
        for user in users:
            try:
                user_chat = await bot.get_chat(chat_id=user.chat_id)
            except TelegramBadRequest:
                continue
            user_dto = EnrichedUserDTO(
                chat_id=user.chat_id,
                username=user_chat.username,
                first_name=user_chat.first_name,
                last_name=user_chat.last_name,
                longest_streak=user.longest_streak,
                last_game_at=user.last_game_at,
                skip_count=user.skip_count,
                wins=user.wins,
                looses=user.looses,
            )
            result.append(user_dto)
        return result

    async def update_user_daily_streak(self, chat_id: int, played_today: bool) -> None:
        user = await self.repository.retrieve_user(chat_id)
        user_dto = UserDTO.from_db(user)
        if played_today:
            user_dto.longest_streak += 1
            user_dto.last_game_at = datetime.date.today()
        else:
            user_dto.skip_count += 1
        await self.repository.update_user(user_dto)

    async def save_game_result(self, chat_id: int, won: bool) -> None:
        user = await self.repository.retrieve_user(chat_id)
        user_dto = UserDTO.from_db(user)
        if won:
            user_dto.wins += 1
        else:
            user_dto.looses += 1
        await self.repository.update_user(user_dto)

    async def get_user_statistics(self, chat_id: int) -> UserStatisticsDTO | None:
        statistics = await self.repository.get_user_statistics(chat_id)
        return statistics
