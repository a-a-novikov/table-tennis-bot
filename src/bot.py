import asyncio
import pytz
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.client import Redis

from config import settings
from dispatcher import get_dispatcher, get_redis_storage
from handlers.after_daily import send_daily_invitation, send_paired_players_list, \
    send_save_game_result_messages


async def setup_periodic_tasks(bot):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Novosibirsk"))

    # after-daily crons
    scheduler.add_job(send_daily_invitation, "cron", hour=13, minute=50, args=(bot,))
    scheduler.add_job(send_paired_players_list, "cron", hour=14, minute=35, args=(bot,))
    scheduler.add_job(send_save_game_result_messages, "cron", hour=15, minute=15, args=(bot,))

    scheduler.start()


async def start_bot():
    bot = Bot(token=settings.BOT_TOKEN)
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
    await setup_periodic_tasks(bot)
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == '__main__':
    logging.basicConfig(level=settings.LOGGING_LEVEL)
    asyncio.run(start_bot())
