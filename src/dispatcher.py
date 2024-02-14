"""This file contains build dispatcher logic."""

from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from redis.asyncio.client import Redis

from config import settings

from handlers import start, after_daily, announce, couple_tourney, personal_stats


def get_redis_storage(
    redis: Redis, state_ttl=settings.REDIS_STATE_TTL, data_ttl=settings.REDIS_DATA_TTL
):
    """This function create redis storage or get it forcely from configuration.

    :param redis: Redis client instance
    :param state_ttl: FSM State Time-To-Delete timer in seconds (has effect only
    for Redis database)
    :param data_ttl: FSM Data Time-To-Delete timer in seconds (has effect only
    for Redis database)
    :return: Created Redis storage.
    """
    return RedisStorage(redis=redis, state_ttl=state_ttl, data_ttl=data_ttl)


def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: FSMStrategy | None = FSMStrategy.CHAT,
    event_isolation: BaseEventIsolation | None = None,
):
    """This function set up dispatcher with routers, filters and middlewares."""
    dp = Dispatcher(
        storage=storage,
        fsm_strategy=fsm_strategy,
        events_isolation=event_isolation,
    )

    dp.include_router(start.router)
    dp.include_router(after_daily.router)
    dp.include_router(couple_tourney.router)
    dp.include_router(announce.router)
    dp.include_router(personal_stats.router)

    # Register middlewares

    return dp
