

def cron_exp_to_scheduler_kwargs(exp: str) -> dict[str, str]:
    """
    Преобразует exp формата crontab в именнованные входные аргументы для AsyncIOScheduler.add_job
    """
    minute, hour, day, month, day_of_week = exp.split(" ")
    return {
        "trigger": "cron",
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "day_of_week": day_of_week,
    }
