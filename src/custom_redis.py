from abc import ABC

from config import settings
from redis.asyncio.client import Redis


class RedisClient(Redis, ABC):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(RedisClient, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(
            db=settings.REDIS_DATABASE,
            host=settings.REDIS_HOST,
            password=settings.REDIS_PASSWORD,
            username=settings.REDIS_USERNAME,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )


redis: RedisClient = RedisClient()
