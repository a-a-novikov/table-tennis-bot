import asyncio
import pytz
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio.client import Redis

from config import settings
from dispatcher import get_dispatcher, get_redis_storage
from handlers import after_daily
from utils.cron import cron_exp_to_scheduler_kwargs


async def setup_periodic_tasks(bot):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Novosibirsk"))

    # after-daily crons
    scheduler.add_job(
        func=after_daily.send_daily_invitation,
        args=(bot,),
        **cron_exp_to_scheduler_kwargs(settings.AFTER_DAILY_INVITATION_CRON),
    )
    scheduler.add_job(
        func=after_daily.send_paired_players_list,
        args=(bot,),
        **cron_exp_to_scheduler_kwargs(settings.AFTER_DAILY_PAIRED_PLAYERS_LIST_CRON),
    )
    scheduler.add_job(
        func=after_daily.send_save_game_result_messages,
        args=(bot,),
        **cron_exp_to_scheduler_kwargs(settings.AFTER_DAILY_RESULT_SURVEY_CRON),
    )

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
