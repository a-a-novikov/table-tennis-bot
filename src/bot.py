import asyncio
import logging

from aiogram import Bot
from redis.asyncio.client import Redis

from config import settings
from dispatcher import get_dispatcher, get_redis_storage
from periodic_tasks import setup_periodic_tasks
from utils.retry_on_exc import get_retrying_bot


async def start_bot():
    bot = Bot(token=settings.BOT_TOKEN)
    retrying_bot = get_retrying_bot(
        bot=bot,
        retries=settings.BOT_MAX_RETRIES,
        delay=settings.BOT_DELAY_BETWEEN_RETRIES,
    )
    storage = get_redis_storage(
        redis=Redis(
            db=settings.REDIS_DATABASE,
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASSWORD,
            username=settings.REDIS_USERNAME,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    )
    dp = get_dispatcher(storage=storage)
    await setup_periodic_tasks(retrying_bot)
    await dp.start_polling(
        retrying_bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == '__main__':
    logging.basicConfig(level=settings.LOGGING_LEVEL)
    asyncio.run(start_bot())
