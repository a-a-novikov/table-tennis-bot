from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    pass

TESTING = True


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DATABASE: str
    REDIS_USERNAME: str | None
    REDIS_PASSWORD: str | None
    REDIS_DATA_TTL: int
    REDIS_STATE_TTL: int
    BOT_TOKEN: str
    POSTGRES_DSN: str
    DEBUG: bool = False
    LOGGING_LEVEL: int = 1
    ADMIN_CHAT_IDS: list[int] = []

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
