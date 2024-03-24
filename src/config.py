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

    AFTER_DAILY_INVITATION_CRON: str
    AFTER_DAILY_PAIRED_PLAYERS_LIST_CRON: str
    AFTER_DAILY_RESULT_SURVEY_CRON: str

    BOT_TOKEN: str
    BOT_MAX_RETRIES: int = 5
    BOT_DELAY_BETWEEN_RETRIES: float = 0.2
    ADMIN_CHAT_IDS: list[int] = []

    POSTGRES_DSN: str

    DEBUG: bool = False
    LOGGING_LEVEL: int = 1

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
