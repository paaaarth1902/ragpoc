from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict( # how to and where from to read config
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"

    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["INFO", "ERROR", "DEBUG", "WARNING"] = "INFO"

    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str
    database_url: str

@lru_cache
def get_settings() -> Settings:
    return Settings()

