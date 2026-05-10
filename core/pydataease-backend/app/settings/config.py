from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    app_name: str = "DataEase API"
    version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://dataease:dataease@localhost:5432/dataease"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 1800
    secret_key: str = "change-me-in-production"
    share_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    api_prefix: str = "/de2api"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(env_file=".env", env_prefix="DE_")


class DevConfig(BaseConfig):
    debug: bool = True
    database_url: str = "postgresql+asyncpg://dataease:dataease@localhost:5432/dataease"


class ProdConfig(BaseConfig):
    debug: bool = False


_settings: BaseConfig | None = None


def get_settings() -> BaseConfig:
    global _settings
    if _settings is None:
        import os

        env = os.getenv("DE_ENV", "dev")
        if env == "prod":
            _settings = ProdConfig()
        else:
            _settings = DevConfig()
    return _settings
