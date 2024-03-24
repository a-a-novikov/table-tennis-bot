import asyncio
import time
from typing import Callable, Any

from aiogram import Bot

import constants


def async_retry_on_exc(retries: int = 3, delay: float = 0.2) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]):
        async def wrapper(*args, **kwargs):
            print("Loool")
            for retry_num in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if retry_num == retries - 1:
                        raise e
                    else:
                        await asyncio.sleep(delay)
        return wrapper
    return decorator


def retry_on_exc(retries: int = 3, delay: float = 0.2) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            for retry_num in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retry_num == retries - 1:
                        raise e
                    else:
                        time.sleep(delay)
        return wrapper
    return decorator


def get_retrying_bot(bot: Bot, retries: int, delay: float) -> Bot:
    for method_name in constants.BOT_METHODS_TO_RETRY_ASYNC:
        decorator = async_retry_on_exc(retries, delay)
        setattr(bot, method_name, decorator(getattr(bot, method_name)))
    for method_name in constants.BOT_METHODS_TO_RETRY:
        setattr(bot, method_name, retry_on_exc(retries, delay))
    return bot
