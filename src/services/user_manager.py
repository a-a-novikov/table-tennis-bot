from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
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
        return user

    async def get_user(self, chat_id: int) -> UserDTO | None:
        return await self.repository.retrieve_user(chat_id)

    async def update_user(self, user: UserDTO) -> UserDTO | None:
        return await self.repository.update_user(user)

    async def get_user_enriched(self, chat_id: int, bot: Bot) -> EnrichedUserDTO | None:
        user = await self.repository.retrieve_user(chat_id)
        try:
            user_chat = await bot.get_chat(chat_id=user.chat_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            return None
        return EnrichedUserDTO(
            chat_id=user.chat_id,
            title_poky_id=user.title_poky_id,
            username=user_chat.username,
            first_name=user_chat.first_name,
            last_name=user_chat.last_name,
        )

    async def get_all_users(self) -> list[UserDTO]:
        return await self.repository.retrieve_all_users()
    
    async def get_all_users_enriched(self, bot: Bot) -> list[EnrichedUserDTO]:
        users = await self.repository.retrieve_all_users()
        result = []
        for user in users:
            try:
                user_chat = await bot.get_chat(chat_id=user.chat_id)
            except (TelegramBadRequest, TelegramForbiddenError):
                continue
            user_dto = EnrichedUserDTO(
                chat_id=user.chat_id,
                title_poky_id=user.title_poky_id,
                username=user_chat.username,
                first_name=user_chat.first_name,
                last_name=user_chat.last_name,
            )
            result.append(user_dto)
        return result

    async def get_user_statistics(self, chat_id: int) -> UserStatisticsDTO | None:
        statistics = await self.repository.get_user_statistics(chat_id)
        return statistics
