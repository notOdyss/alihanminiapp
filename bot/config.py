from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    BOT_TOKEN: str
    LOG_BOT_TOKEN: str
    LOG_CHAT_ID: int

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/alihanbot"

    ADMIN_IDS: list[int] = []

    WEBAPP_URL: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def db_url_asyncpg(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
