import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
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
